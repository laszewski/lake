# Eagle Shot Planner

Use this interactive tool to plan your shot based on your gear and the distance to the eagle.

<div id="calculator-container" style="font-family:sans-serif; max-width:800px; margin:20px auto; padding:20px; border:1px solid #ddd; border-radius:15px; background:#fff; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:20px; margin-bottom:30px;">
    
    <!-- Inputs -->
    <div style="display:flex; flex-direction:column; gap:15px;">
      <div>
        <label style="display:block; font-weight:bold; margin-bottom:5px;">
          Camera System
        </label>
        <select id="selectedGear" style="width:100%; padding:8px; border-radius:5px; border:1px solid #ccc;">
          <option value="Sony A1 II FF">Sony A1 II FF</option>
          <option value="Canon R5 II FF">Canon R5 II FF</option>
          <option value="Sony A7 V FF">Sony A7 V FF</option>
          <option value="Canon R7 APS-C">Canon R7 APS-C</option>
          <option value="Canon EOS R10 APS-C">Canon EOS R10 APS-C</option>
          <option value="OM System M4/3">OM System M4/3</option>
        </select>
      </div>

      <div>
        <label style="display:block; font-weight:bold; margin-bottom:5px;">
          Focal Length (mm): <span id="val-focal">600</span>mm
        </label>
        <input type="range" id="focalLength" min="400" max="800" step="100" value="600" style="width:100%;">
      </div>

      <div>
        <label style="display:block; font-weight:bold; margin-bottom:5px;">
          Distance to Bird (m)
        </label>
        <input type="number" id="distance" value="100" min="10" max="500" style="width:100%; padding:8px; border-radius:5px; border:1px solid #ccc;">
      </div>

      <div>
        <label style="display:block; font-weight:bold; margin-bottom:5px;">
          Aperture (f-stop): f/<span id="val-fstop">5.6</span>
        </label>
        <input type="range" id="fStop" min="2.8" max="22" step="0.1" value="5.6" style="width:100%;">
      </div>

      <div>
        <label style="display:block; font-weight:bold; margin-bottom:5px;">
          Light Condition
        </label>
        <select id="lightCondition" style="width:100%; padding:8px; border-radius:5px; border:1px solid #ccc;">
          <option value="Bright Sun">Bright Sun</option>
          <option value="Overcast">Overcast</option>
          <option value="Golden Hour">Golden Hour</option>
          <option value="Deep Shade">Deep Shade</option>
        </select>
      </div>
    </div>

    <!-- Results -->
    <div style="display:grid; gap:20px;">
      <div style="padding:20px; border:1px solid #ddd; border-radius:10px; background:#f9f9f9; text-align:center;">
        <div style="font-size:0.9em; color:#666;">Frame Fill</div>
        <div id="res-fill" style="font-size:2em; font-weight:bold; color:#2c3e50;">--%</div>
      </div>

      <div style="padding:20px; border:1px solid #ddd; border-radius:10px; background:#f9f9f9; text-align:center;">
        <div style="font-size:0.9em; color:#666;">Depth of Field</div>
        <div id="res-dof" style="font-size:2em; font-weight:bold; color:#2c3e50;">-- m</div>
      </div>

      <div style="padding:20px; border:1px solid #ddd; border-radius:10px; background:#f9f9f9; text-align:center;">
        <div style="font-size:0.9em; color:#666;">Suggested ISO</div>
        <div id="res-iso" style="font-size:2em; font-weight:bold; color:#2c3e50;">--</div>
      </div>
    </div>
  </div>

  <div id="diffraction-warning" style="display:none; padding:15px; background:#fff3cd; border:1px solid #ffeeba; color:#856404; border-radius:10px; text-align:center; font-weight:bold;">
    ⚠️ Diffraction Warning: At this aperture, image sharpness may soften due to diffraction.
  </div>
</div>

<script>
(function () {
  const gear = {
    "Sony A1 II FF": { h: 24, mp: 50, coc: 0.03 },
    "Canon R5 II FF": { h: 24, mp: 45, coc: 0.03 },
    "Sony A7 V FF": { h: 24, mp: 33, coc: 0.03 },
    "Canon R7 APS-C": { h: 15, mp: 32.5, coc: 0.02 },
    "Canon EOS R10 APS-C": { h: 15, mp: 24.2, coc: 0.02 },
    "OM System M4/3": { h: 13, mp: 20, coc: 0.015 }
  };

  const lightMap = {
    "Bright Sun": 15,
    "Overcast": 12,
    "Golden Hour": 10,
    "Deep Shade": 7
  };

  const birdHeight = 0.9;
  const targetShutter = 1 / 2000;

  function update() {
    const selectedGear = document.getElementById("selectedGear").value;
    const focalLength = parseFloat(document.getElementById("focalLength").value);
    const distance = parseFloat(document.getElementById("distance").value);
    const fStop = parseFloat(document.getElementById("fStop").value);
    const lightCondition = document.getElementById("lightCondition").value;

    document.getElementById("val-focal").innerText = focalLength;
    document.getElementById("val-fstop").innerText = fStop;

    // Frame Fill
    const sensorHeight = gear[selectedGear].h / 1000;
    const fillRatio = ((focalLength / 1000) * birdHeight) / (distance * sensorHeight);
    document.getElementById("res-fill").innerText = (fillRatio * 100).toFixed(1) + "%";

    // Depth of Field
    const fMeters = focalLength / 1000;
    const coc = gear[selectedGear].coc / 1000;
    const dof = (2 * fStop * coc * Math.pow(distance, 2)) / Math.pow(fMeters, 2);
    document.getElementById("res-dof").innerText = dof.toFixed(2) + " m";

    // ISO estimate using EV100 system
    const ev100 = lightMap[lightCondition];
    const iso = 100 * (Math.pow(fStop, 2) * (1 / targetShutter)) / Math.pow(2, ev100);
    const standardIsos = [100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200];
    const closestIso = standardIsos.reduce((prev, curr) => 
      Math.abs(curr - iso) < Math.abs(prev - iso) ? curr : prev
    );
    document.getElementById("res-iso").innerText = closestIso;

    // Diffraction estimate
    const pixelPitch = gear[selectedGear].h * 1000 / Math.sqrt(gear[selectedGear].mp * 1000000);
    const airyDisk = 2.44 * 0.55 * fStop;
    document.getElementById("diffraction-warning").style.display = airyDisk > pixelPitch ? "block" : "none";
  }

  document.querySelectorAll("#calculator-container input, #calculator-container select").forEach(el => {
    el.addEventListener("input", update);
  });

  update();
})();
</script>