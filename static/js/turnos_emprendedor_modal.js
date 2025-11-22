
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


// TODO: Hacer que se limpien los campos del formulario
/**
 * Cierra el modal de turnos, y limpia los datos ingresados en el formulario.
 */
const cerrarModalTurnos = () => {
  document.getElementById("modal-turnos").classList.add("hidden");
  document.body.style.overflow = "";
}

/**
 * Inicializar el datepicker, limpia también los horarios
 */
const iniciarDatePicker = () => {
  flatpickr("#input-fecha", {
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
      <div class="w-full h-full flex items-center gap-2 px-2 py-1 -m-2 rounded peer-checked:border peer-checked:border-sky-700">
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
      <p class="w-full h-full flex items-center gap-2 px-2 py-1 -m-2 rounded peer-checked:border peer-checked:border-sky-700">${h}</p>
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

  if (idTurno) {
    /* {% comment %} Se está editando un turno, hay que hacer el get de los datos {% endcomment %}
        {% comment %} Habría que: {% endcomment %}
        {% comment %} 1. Cambiar el título {% endcomment %}
        {% comment %} 2. Hacer el get de los datos del turno {% endcomment %}
        {% comment %} 3. Poblar el formulario con los datos del turno {% endcomment %}
        {% comment %} 4. Mostrar el botón de eliminar con un formulario {% endcomment %}
    */


  } else {
     // Primero hay que cambiar la action del form para que se pueda hacer un submit directamente
     // Esto viene desde el tempalte
     formulario.action = urlActionCrear;

  }
  document.getElementById("modal-turnos").classList.remove("hidden");
}

const handleSubmit = (e) => {
  e.preventDefault();
  alert("Se submiteó el form");
}

const cargarHorariosDisponibles = async (idServicio, fechaSolicitada) => {
    const url = urlCargarHorariosDisponibles
      .replace("0/", `${idServicio}/`)
      .replace("placeholder", fechaSolicitada);

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