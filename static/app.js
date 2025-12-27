let currentDate = null; // base date for current week (Date object)
let dailyChart = null;

function isoToDate(s) {
  return new Date(s + "T00:00:00");
}

function formatWeekLabel(startIso, endIso) {
  const a = new Date(startIso), b = new Date(endIso);
  return a.toLocaleDateString() + " - " + b.toLocaleDateString();
}

function renderTable(data) {
  const days = data.days;
  const habits = data.habits;
  let html = "";

  // Table header
  html += "<thead class='table-light'><tr><th>Habit</th>";
  days.forEach(d => {
    const dt = new Date(d + "T00:00:00");
    const day = dt.toLocaleDateString(undefined, { weekday: 'short' });
    html += `<th class="text-center">${day}<br/><small>${dt.toLocaleDateString()}</small></th>`;
  });
  html += `<th class="text-center">Weekly<br/>Total</th></tr></thead>`;
  html += "<tbody>";

  if (habits.length === 0) {
    html += `<tr><td colspan="${days.length + 2}" class="py-4 text-muted text-center">
              No habits found
            </td></tr>`;
  } else {
    habits.forEach(h => {
      html += `<tr data-habit-id="${h.id}">
                <td class="align-middle">${h.name}</td>`;

      days.forEach(d => {
        const val = h.entries[d] || 0;
        const checked = val > 0 ? "table-success" : "";
        html += `<td class="text-center cell ${checked}"
                      data-date="${d}"
                      data-habit="${h.id}">
                    <button class="btn btn-sm btn-outline-secondary toggleBtn">
                      ${val > 0 ? "✓" : ""}
                    </button>
                 </td>`;
      });

      html += `<td class="text-center align-middle">
                <div class="h5 mb-0">${h.weekly_total}</div>
                <div class="small text-muted">
                  ${Math.round(h.weekly_total / 7 * 100)}%
                </div>
               </td></tr>`;
    });
  }

  html += "</tbody>";
  $("#habitTable").html(html);

  // Toggle handler
  $(".cell").off("click").on("click", function () {
    const date = $(this).data("date");
    const habit = $(this).data("habit");
    const isOn = $(this).hasClass("table-success");
    const newVal = isOn ? 0 : 1;

    $.ajax({
      url: "/api/entry",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        habit_id: habit,
        date: date,
        value: newVal
      })
    }).done(function () {
      loadWeek(currentDate);
    });
  });
}

function loadWeek(baseDate) {
  const dateStr = baseDate ? baseDate.toISOString().slice(0, 10) : null;

  // 🔍 SEARCH PARAM (NEW)
  const search = document.getElementById("searchInput")?.value || "";

  let url = "/api/week";
  const params = [];

  if (dateStr) params.push(`date=${dateStr}`);
  if (search) params.push(`search=${encodeURIComponent(search)}`);

  if (params.length > 0) {
    url += "?" + params.join("&");
  }

  $.getJSON(url).done(function (data) {
    currentDate = new Date(data.start + "T00:00:00");
    $("#weekLabel").text(formatWeekLabel(data.start, data.end));
    renderTable(data);
    renderChart(data.days, data.daily_sums);
  });
}

function renderChart(days, sums) {
  const labels = days.map(d =>
    new Date(d + "T00:00:00").toLocaleDateString(undefined, { weekday: 'short' })
  );

  const ctx = document.getElementById("dailyChart").getContext("2d");
  if (dailyChart) dailyChart.destroy();

  dailyChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Daily Completions",
        data: sums,
        fill: false,
        tension: 0.2,
        pointRadius: 6,
        borderWidth: 2
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: Math.max(5, Math.max(...sums) + 1)
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

$(function () {
  // Initial load
  loadWeek(null);

  $("#addHabitBtn").on("click", function () {
    const name = $("#newHabitInput").val().trim();
    if (!name) return alert("Enter habit name");

    $.ajax({
      url: "/api/habit",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ name: name })
    }).done(function () {
      $("#newHabitInput").val("");
      loadWeek(currentDate);
    });
  });

  $("#prevWeek").on("click", function () {
    if (!currentDate) currentDate = new Date();
    currentDate.setDate(currentDate.getDate() - 7);
    loadWeek(currentDate);
  });

  $("#nextWeek").on("click", function () {
    if (!currentDate) currentDate = new Date();
    currentDate.setDate(currentDate.getDate() + 7);
    loadWeek(currentDate);
  });
});
