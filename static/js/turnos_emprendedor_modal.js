
let diasQueTrabaja = [];
/**
 * Obtener los dias que trabaja un emprendedor, para así poder bloquear
 * en el calendario las fechas que no se puede sacar turno.
 * @returns {Array} El array de enteros [0..6] representando los días de la semana que trabaja el emprendedor.
 */
const obtenerDiasQueTrabaja = async () => {
  try {
    // Esto viene desde el template de django
    const response = await fetch(urlObtenerDiasQueTrabaja, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error en la respuesta: ${response.status}`);
    }

    const data = await response.json();

    console.log(`Dias trabajados: ${data.dias_trabajados}`);
    return data.dias_trabajados;

  } catch (error) {
    console.error('Error al obtener días trabajados:', error);
    return [];
  }
}


let serviciosEmprendedor = [];
/**
 * Obtener todos los servicios que ofrece el emprendedor
 * @returns {Array} El array con lso servicios del emprendedor.
 */
const obtenerServiciosEmprendedor = async () => {
  try {
    // Esto viene desde el template de django
    const response = await fetch(urlObtenerServiciosEmprendedor, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error en la respuesta: ${response.status}`);
    }

    const data = await response.json();

    return data.servicios || [];

  } catch (error) {
    console.error('Error al obtener servicios:', error);
    return [];
  }
}


/**
 * Cierra el modal de turnos, y limpia los datos ingresados en el formulario.
 */
const cerrarModalTurnos = () => {
  document.getElementById("modal-turnos").classList.add("hidden");
  document.body.style.overflow = "";

  // Limpiar todos los inputs
  limpiarInputs();
  limpiarHorarios();
  limpiarServicios();
}

var fpFecha;
/**
 * Inicializar el datepicker, limpia también los horarios
 */
const iniciarDatePicker = () => {
  fpFecha = flatpickr("#input-fecha", {
    altInput: true,
    altFormat: "j \\d\\e F, Y",
    dateFormat: "Y-m-d",
    locale: "es",
    enable: [
      function(fecha) {
        // El back cuenta el lunes como día cero, pero el picker cuenta el domingo como dia cero
        return diasQueTrabaja.includes((fecha.getDay() + 6) % 7);
      }
    ],
    onChange: function() {limpiarHorarios(); iniciarServicios();}
  });
}

/**
 * Construir el html para el selector de servicios.
 */
const iniciarServicios = () => {
  const contenedor = document.getElementById("listado-servicios");
  limpiarServicios();

  serviciosEmprendedor.forEach(s => {
    const precioTexto = s.precio
              ? `· $${Number(s.precio).toLocaleString("es-AR")}`
              : "· Gratuito";

    const wrapper = document.createElement("label");
    wrapper.className = "flex items-center gap-4 p-2 rounded cursor-pointer hover:bg-slate-50";

    wrapper.innerHTML = `
      <input type="radio" name="servicio" value="${s.id}" class="hidden peer" onclick="handleObtenerHorarios(${s.id})">
      <div class="w-full h-full flex items-center gap-2 px-2 py-1 -m-2 rounded peer-checked:border peer-checked:border-sky-700 peer-checked:bg-gray-50">
        <div class="relative w-3 h-3 rounded-full shadow" style="background:${s.color}">
          <div class="absolute inset-0 rounded-full border" 
              style="border-color:${s.color}; filter:brightness(0.8);"></div>
        </div>
        <div>
          <p class="font-medium text-slate-900">${s.nombre}</p>
          <p class="text-xs text-slate-500">${s.duracion} minutos ${precioTexto}</p>
        </div>
      </div>
    `;

    contenedor.appendChild(wrapper);
  });

  // Hay que marcarlo como required para que se pueda enviar el formulario sin problemas
  const primerRadio = contenedor.querySelector('input[type="radio"]');

  if (primerRadio) {
    primerRadio.required = true;
  }
}

const limpiarHorarios = () => {
  const contenedor = document.getElementById("listado-horarios");
  while (contenedor.firstChild) {contenedor.removeChild(contenedor.lastChild);}
}

const limpiarServicios = () => {
  const contenedor = document.getElementById("listado-servicios");
  while (contenedor.firstChild) {contenedor.removeChild(contenedor.lastChild);}
}

/**
 * Genera el html para los horarios, toma una lista de horarios.
 * @param {Array} horarios La lista de horarios disponibles devuelta por el back
 */
const iniciarHorarios = (horarios) => {
  const contenedor = document.getElementById("listado-horarios");

  limpiarHorarios();

  horarios.forEach(h => {

    const wrapper = document.createElement("label");
    wrapper.className = "flex items-center gap-4 p-2 rounded cursor-pointer hover:bg-slate-50";

    wrapper.innerHTML = `
      <input type="radio" name="hora" value="${h}" class="hidden peer">
      <p class="w-full h-full flex items-center gap-2 px-2 py-1 -m-2 rounded peer-checked:border peer-checked:border-sky-700 peer-checked:bg-gray-50">${h}</p>
    `;

    contenedor.appendChild(wrapper);
  });

  // Hay que marcarlo como required para que se pueda enviar el formulario sin problemas
  const primerRadio = contenedor.querySelector('input[type="radio"]');

  if (primerRadio) {
    primerRadio.required = true;
  }
}

const mostrarModalTurnos = async (idTurno = null) => {
  // {% comment %} Esto se tiene que hacer para que no se mueva la pagina de atras cuando se hace scroll en el modal {% endcomment %}
  document.body.style.overflow = "hidden";
  const formulario = document.getElementById("formulario");
  const tituloModal = document.getElementById("modal-titulo");
  const botonConfirmar = document.getElementById("btn-confirmar");
  
  if (idTurno) {
    tituloModal.innerHTML = "Editar turno";
    botonConfirmar.innerHTML = "Guardar";
    formulario.action = urlActionEditar.replace("0", idTurno);

    /**
     * Hay que inicializar los servicios antes de poder mostrar el modal, porque
     * si no, no se puede seleccionar la input que tiene el servicio seleccionado.
     * Una vez que se selecciona eso, también hay que seleccionar el horario de nuevo,
     * haciendo una request al endpoint. El endpoint tiene que ser capaz de saber cuándo
     * está editando y entonces no tomar en cuenta el turno actual cuando
     * calcula los horarios disponibles.
     */

    iniciarServicios();
    // 1. Buscar el turno por id
    var objetoTurno;
    if (!window.turnosEmprendedor || !Array.isArray(window.turnosEmprendedor)) {
      const turnos = await obtenerTurnosEmprendedor();
      objetoTurno = turnos.find(t => t.id === idTurno);
      console.error(`No estaba, se lo trajo de ${turnos}`)
    } else {
      objetoTurno = window.turnosEmprendedor.find(t => t.id == idTurno);
    }

    const dtInicioTurno = new Date(objetoTurno.turno.inicio);
    const fechaInicioTurno = dtInicioTurno.toISOString().split("T")[0];

    // 1.1 Obtener todas las inputs
    
    const horas = dtInicioTurno.getHours().toString().padStart(2, "0");
    const minutos = dtInicioTurno.getMinutes().toString().padStart(2, "0");
    const horaInicio = `${horas}:${minutos}`;
    //TODO: Si el turno se sacó en una fecha que ya no se trabaja, el evento select del flatpickr reinicia todo
    //TODO: Asegurarse de que no se pueda enviar si no se tiene completos los campos
    //TODO: Si se hace click en un evento de la vista de ver más, no se cierra la vista de ver más.

    // Esto siempre se puede hacer porque los servicios van a estar cargados y tienen on_delete cascade
    // asi que no hay que preocuparse por qué hacer si no existe el servicio
    const servicioInput = document.querySelector(`input[name="servicio"][value="${objetoTurno.servicio.id}"]`);
    servicioInput.checked = true;

    // Una vez chequeado, hay que cargar los horarios, y acá es donde la vista tiene que 
    // asegurarse de que si se está editando, se devuelvan los horarios como si no existiera
    // el turno actual
    iniciarHorarios(
      await cargarHorariosDisponibles(
        idServicio = objetoTurno.servicio.id,
        fechaSolicitada= fechaInicioTurno,
        idTurno= objetoTurno.id
      )
    );
    
    // Una vez cargados los horarios, se tiene que seleccionar el del turno.
    // Si no existe, no se selecciona, y como es required, falla el submit, obligando a la persona a seleccionar un horario nuevo.
    const horaInput = document.querySelector(`input[name="hora"][value="${horaInicio}"]`);
    if (horaInput) {
      horaInput.checked = true;
    }

    const inputCliente = document.getElementById("input-cliente");
    const inputClienteContacto = document.getElementById("input-cliente-contacto");
    const inputNota = document.getElementById("input-nota");
    const inputIdCliente = document.getElementById("input-id-cliente");

    if (inputIdCliente.value){
      // Si la input de la id del cliente tiene valor, entonces es porque fue el cliente quien sacó el turno
      // y no se puede cambiar el nombre ni el contacto
      inputCliente.disabled = true;
      inputClienteContacto.disabled = true;
      inputNota.disabled = true;

      inputCliente.classList.add("cursor-not-allowed");
      inputClienteContacto.classList.add("cursor-not-allowed");
      inputNota.classList.add("cursor-not-allowed");
    } else {
      inputCliente.disabled = false;
      inputClienteContacto.disabled = false;
      inputNota.disabled = false;

      inputCliente.classList.add("cursor-text");
      inputClienteContacto.classList.add("cursor-text");
      inputNota.classList.add("cursor-text");
    }

    inputCliente.value = objetoTurno.cliente.nombre;
    inputClienteContacto.value = objetoTurno.cliente.contacto;
    inputNota.value = objetoTurno.turno.nota;
    inputIdCliente.value = objetoTurno.cliente.id;

    // 3. cargar los datos al formulario

    // 3.1 Verificar que la fecha del turno esté dentro de los dias que trabaja, por si se edita el horario y no el turno
    if (diasQueTrabaja.includes(dtInicioTurno.getDay())) {
      fpFecha.setDate(fechaInicioTurno);
    } else {
      // La fecha no está dentro de lo que ahora trabaja, hay que obligarlo a seleccionar de nuevo.
    }

  } else {
     // Lo unico que hay que cambiar es la action del form para que se pueda hacer un submit directamente
     // Esto viene desde el tempalte
     formulario.action = urlActionCrear;
     tituloModal.innerHTML = "Nuevo turno";
     botonConfirmar.innerHTML = "Crear";

  }
  document.getElementById("modal-turnos").classList.remove("hidden");
}

const cargarHorariosDisponibles = async (idServicio, fechaSolicitada, idTurno = null) => {

  var url;

  // Se usa la misma logica para obtener los horarios al crear y al editar turnos, solamente se le 
  // pasa la id a la api para que calcule bien los horarios
  if (idTurno != null) {
    url = urlCargarHorariosDisponiblesConTurno
      .replace("0/", `${idServicio}/`)
      .replace("placeholder", fechaSolicitada)
      .replace("9999/", `${idTurno}/`);
  } else {
    url = urlCargarHorariosDisponibles
      .replace("0/", `${idServicio}/`)
      .replace("placeholder", fechaSolicitada);
  }


    console.log(url);

    try {
        const resp = await fetch(url, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            cookies: "include"
        });

        if (!resp.ok) {
            const errorData = await resp.json().catch(() => ({}));
            throw new Error(errorData.error || "Error desconocido del servidor");
        }

        const data = await resp.json();

        if (!data.horarios_disponibles) {
            throw new Error("Respuesta inesperada del servidor");
        }

        return data.horarios_disponibles; // array de strings tipo ["09:00", "09:30", ...]
    } catch (err) {
        console.error("Error cargando horarios:", err.message);
        return [];
    }
}

const handleObtenerHorarios = async (idServicio) => {
  const fecha = document.getElementById("input-fecha").value;

  if (fecha != null) {
    const horarios = await cargarHorariosDisponibles(idServicio, fecha);
    iniciarHorarios(horarios);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  obtenerDiasQueTrabaja()
    .then(result => {
      diasQueTrabaja = result;
      return obtenerServiciosEmprendedor();
    })
    .then(result => {
      serviciosEmprendedor = result;
      iniciarDatePicker();
    })
    .catch(err => console.error(err));
});

function limpiarInputs() {
  const inputCliente = document.getElementById("input-cliente");
  const inputClienteContacto = document.getElementById("input-cliente-contacto");
  const inputNota = document.getElementById("input-nota");
  const inputIdCliente = document.getElementById("input-id-cliente");

  inputCliente.value = "";
  inputClienteContacto.value = "";
  inputNota.value = "";
  inputIdCliente.value = "";
  fpFecha.clear();
}
