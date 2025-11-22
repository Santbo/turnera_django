var calendar;

// TODO: implementar las vistas de hoy, semana y todo eso  https://fullcalendar.io/docs/buttonText
document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
  calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: "es",
    dayMaxEvents: 2,
    headerToolbar: {
      left: 'prev,next,today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    views: {
      timeGrid: {
        eventMinHeight: 25,
        allDaySlot: false,
      }
    },
    eventClick: function(info) {mostrarModalTurnos(info.event.id)}
  });
  calendar.render();
});

var turnosEmprendedor = [];
const obtenerTurnosEmprendedor = async () => {
    try {
      // La url viene del template de django
        const respuesta = await fetch(urlObtenerTurnosEmprendedor, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            },
            // django necesita que le incluyas las cookies porque si no no sabe quien sos 
            credentials: "include"
        });

        if (!respuesta.ok) {
            throw new Error(`Error del servidor: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        turnosEmprendedor = data.turnos;
        return data.turnos;

    } catch (error) {
        console.error("Error al obtener los turnos:", error);
        return [];
    }
}

const obtenerClaseTexto = (colorHex) => {

  // Calcular la formula yiq y cambiar el color: https://stackoverflow.com/a/11868398
    colorHex = colorHex.replace('#', '');

    const r = parseInt(colorHex.substring(0, 2), 16);
    const g = parseInt(colorHex.substring(2, 4), 16);
    const b = parseInt(colorHex.substring(4, 6), 16);

    const yiq = (0.299 * r + 0.587 * g + 0.114 * b);
    return yiq > 128 ? "#000000" : "#FFFFFF";
}

const cargarTurnosAlCalendario = async () => {
  const turnos = await obtenerTurnosEmprendedor();

  turnos.forEach((t) => {
    calendar.addEvent({
      id: t.id,
      allDay: false,
      title: t.servicio.nombre,
      start: t.turno.inicio,
      end: t.turno.fin,
      color: t.servicio.color,
      textColor: obtenerClaseTexto(t.servicio.color),
      display: "block",
      classNames: `cursor-pointer`
    })
  });

  console.log("Cargados turnos");
  calendar.render();
};

const formatearHora = (fechaString) => {
  // Usada en la agenda de hoy para mostrar la hora en 24 horas
    const fecha = new Date(fechaString);
    return fecha.toLocaleTimeString("es-AR", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
    });
}

const formatearFechaLarga = () => {
  // Obtener la fecha de hoy formateada en texto para la agenda de hoy
    return new Date().toLocaleDateString("es-AR", {
        weekday: "long",
        day: "numeric",
        month: "long"
    });
}

const esHoy = (fechaInicioTurno) => {
  // Ver si un turno es de hoy o no
    const d = new Date(fechaInicioTurno);
    const hoy = new Date();
    return (
        d.getFullYear() === hoy.getFullYear() &&
        d.getMonth() === hoy.getMonth() &&
        d.getDate() === hoy.getDate()
    );
}

const renderAgendaHoy = async () => {
  /* renderizar la agenda de hoy, esto puede fallar si se ejecuta antes de que 
  se carguen los turnos, así que hay que llamarla a la función por más de que sea
  ineficiente 
  */

    const cont = document.getElementById("agenda-hoy");
    const turnos = await obtenerTurnosEmprendedor();

    // Filtrar los turnos de hoy  
    const turnosHoy = turnos
      .filter(t => esHoy(t.turno.inicio))
      .sort((a, b) => new Date(a.turno.inicio) - new Date(b.turno.inicio));
      /*
      Esto parece raro pero resulta que así se ordena en js, parecido al sort([], key=) de python
      */

    // Poner el encabezado 
    cont.innerHTML = `
      <div class="flex flex-col h-full">
        <div class="mb-2 font-semibold text-slate-700 shrink-0">
          Agenda de hoy · ${formatearFechaLarga()}
        </div>

        <div id="lista-hoy" class="overflow-auto p-1 grow"></div>
      </div>
    `;

    const lista = document.getElementById("lista-hoy");

    if (turnosHoy.length === 0) {
        lista.innerHTML = `
          <div class="text-sm text-slate-500">No hay turnos para hoy.</div>
        `;
        return;
    }

    const ul = document.createElement("ul");
    ul.className = "divide-y divide-slate-100 overflow-y-auto";

    turnosHoy.forEach(t => {
        const li = document.createElement("li");
        li.className = "py-2 flex items-start gap-3";

        li.innerHTML = `
          <div class="
            h-8 w-12 
            rounded-md 
            ring-1 ring-slate-200 
            grid place-items-center
            bg-[${t.servicio.color}]
            text-xs">
            <p class="font-bold text-[${obtenerClaseTexto(t.servicio.color)}]">${formatearHora(t.turno.inicio)}</p>
          </div>

          <div class="min-w-0 flex-1">
            <div class="text-sm font-medium text-slate-900 truncate">
              ${t.cliente.nombre} · ${t.servicio.nombre}
            </div>

            <div class="text-[11px] text-slate-500">
              ${t.turno.nota ? `Notas: ${t.turno.nota}` : ""}
            </div>
          </div>

          <button
            title="Seleccionar para editar/cancelar"
            onclick="mostrarModalTurnos(${t.id})"
            class="shrink-0 rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-medium hover:bg-slate-50 cursor-pointer"
            data-id="${t.id}"
          >
            Seleccionar
          </button>
        `;

        ul.appendChild(li);
    });

    lista.appendChild(ul);
}



document.addEventListener("DOMContentLoaded", () => {
  cargarTurnosAlCalendario();
  renderAgendaHoy();
});
