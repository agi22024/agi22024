"""
Juego interactivo para Google Colab.
Dos personajes estilo Pokemon (nino y nina de pelo largo)
saltan y corren en una habitacion.

Uso en Colab:
    1. Sube este archivo o copia el contenido en una celda.
    2. Ejecuta: exec(open("game_colab.py").read())
       O simplemente pega todo el contenido en una celda y ejecutala.
"""

from IPython.display import HTML

HTML("""
<style>
  #game-wrapper { text-align: center; font-family: 'Courier New', monospace; }
  #game-canvas { border: 3px solid #222; border-radius: 8px; display: block; margin: 10px auto; image-rendering: pixelated; background: #87CEEB; }
  #game-info { color: #333; margin: 6px auto; max-width: 900px; font-size: 14px; }
  #game-info kbd { background: #eee; border: 1px solid #aaa; border-radius: 3px; padding: 1px 5px; font-size: 12px; }
  #score-board { font-size: 15px; font-weight: bold; margin: 4px; }
</style>
<div id="game-wrapper">
  <div id="score-board">
    <span style="color:#E74C3C;">&#9733; Nino: <span id="score-p1">0</span></span>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    <span style="color:#9B59B6;">&#9733; Nina: <span id="score-p2">0</span></span>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    <span style="color:#F39C12;">&#9734; Estrellas: <span id="stars-left">0</span></span>
  </div>
  <canvas id="game-canvas" width="900" height="560"></canvas>
  <div id="game-info">
    <b>Nino (Rojo):</b> <kbd>A</kbd> <kbd>D</kbd> mover &nbsp; <kbd>W</kbd> saltar
    &nbsp;&nbsp;|&nbsp;&nbsp;
    <b>Nina (Morado):</b> <kbd>&#8592;</kbd> <kbd>&#8594;</kbd> mover &nbsp; <kbd>&#8593;</kbd> saltar
    <br>Recoge las estrellas doradas. &#127775; Presiona <kbd>R</kbd> para reiniciar.
  </div>
</div>

<script>
(function() {
  const canvas = document.getElementById('game-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  // --- Room ---
  const FLOOR_Y = H - 60;
  const GRAVITY = 0.55;

  // --- Furniture / room elements ---
  const furniture = [
    { type: 'shelf', x: 50, y: 150, w: 140, h: 18 },
    { type: 'shelf', x: 710, y: 150, w: 140, h: 18 },
    { type: 'platform', x: 270, y: 310, w: 150, h: 18 },
    { type: 'platform', x: 480, y: 230, w: 150, h: 18 },
    { type: 'platform', x: 100, y: 370, w: 130, h: 18 },
    { type: 'platform', x: 670, y: 370, w: 130, h: 18 },
    { type: 'table', x: 370, y: FLOOR_Y - 55, w: 160, h: 55 },
  ];

  // --- Stars ---
  let stars = [];
  function spawnStars() {
    stars = [];
    const positions = [
      { x: 120, y: 125 }, { x: 780, y: 125 },
      { x: 345, y: 285 }, { x: 555, y: 205 },
      { x: 165, y: 345 }, { x: 735, y: 345 },
      { x: 450, y: FLOOR_Y - 80 },
      { x: 60, y: FLOOR_Y - 25 }, { x: 840, y: FLOOR_Y - 25 },
      { x: 450, y: 110 },
    ];
    positions.forEach(p => stars.push({ x: p.x, y: p.y, r: 13, alive: true, blink: 0 }));
    document.getElementById('stars-left').textContent = stars.filter(s => s.alive).length;
  }

  // --- Characters ---
  function createPlayer(name, color, hairColor, startX, controls) {
    return {
      name, color, hairColor,
      x: startX, y: FLOOR_Y, w: 40, h: 50,
      vx: 0, vy: 0,
      onGround: true,
      facing: 1,
      frame: 0, frameTick: 0,
      score: 0,
      controls,
      keysDown: {},
    };
  }

  const P1 = createPlayer('Nino', '#E74C3C', '#4A2A0A', 140, { left: 'a', right: 'd', jump: 'w' });
  const P2 = createPlayer('Nina', '#9B59B6', '#5D3FD3', 720, { left: 'arrowleft', right: 'arrowright', jump: 'arrowup' });
  const players = [P1, P2];

  // --- Input ---
  const keysDown = {};
  document.addEventListener('keydown', e => {
    const k = e.key.toLowerCase();
    keysDown[k] = true;
    if (['arrowup','arrowdown','arrowleft','arrowright','w','a','d',' '].includes(k)) e.preventDefault();
    if (k === 'r') resetGame();
  });
  document.addEventListener('keyup', e => { keysDown[e.key.toLowerCase()] = false; });

  // --- Drawing helpers ---
  function drawPixelChar(p) {
    const { x, y, w, h, color, hairColor, facing, frame, onGround } = p;
    const cx = x, cy = y;
    const dir = facing;

    // Bounce when running
    const bounce = (!onGround) ? 0 : (frame % 2 === 0 && Math.abs(p.vx) > 0.5) ? -3 : 0;
    const dy = cy + bounce;

    // --- Shadow ---
    ctx.fillStyle = 'rgba(0,0,0,0.13)';
    ctx.beginPath();
    ctx.ellipse(cx, FLOOR_Y + 3, 22, 7, 0, 0, Math.PI * 2);
    ctx.fill();

    // --- Hair (long, behind body) ---
    ctx.fillStyle = hairColor;
    // back hair flowing down
    const hairLen = 32;
    ctx.beginPath();
    ctx.moveTo(cx - 14 * dir, dy - h + 6);
    ctx.quadraticCurveTo(cx - 20 * dir, dy - h + hairLen, cx - 12 * dir, dy - h + hairLen + 8);
    ctx.lineTo(cx - 3 * dir, dy - h + hairLen + 6);
    ctx.lineTo(cx - 6 * dir, dy - h + 8);
    ctx.closePath();
    ctx.fill();
    // other side hair
    ctx.beginPath();
    ctx.moveTo(cx + 14 * dir, dy - h + 6);
    ctx.quadraticCurveTo(cx + 20 * dir, dy - h + hairLen, cx + 12 * dir, dy - h + hairLen + 8);
    ctx.lineTo(cx + 3 * dir, dy - h + hairLen + 6);
    ctx.lineTo(cx + 6 * dir, dy - h + 8);
    ctx.closePath();
    ctx.fill();

    // --- Body ---
    ctx.fillStyle = color;
    const bodyTop = dy - h + 20;
    ctx.fillRect(cx - 10, bodyTop, 20, 22);

    // --- Head ---
    ctx.fillStyle = '#FDDCB5';
    ctx.beginPath();
    ctx.arc(cx, dy - h + 14, 15, 0, Math.PI * 2);
    ctx.fill();

    // --- Hair top ---
    ctx.fillStyle = hairColor;
    ctx.beginPath();
    ctx.arc(cx, dy - h + 10, 17, Math.PI, Math.PI * 2);
    ctx.fill();
    // bangs
    ctx.fillRect(cx - 16, dy - h + 5, 32, 7);

    // --- Eyes (Pokemon style - big!) ---
    const eyeOff = 5 * dir;
    // white
    ctx.fillStyle = '#FFF';
    ctx.beginPath();
    ctx.ellipse(cx - 5 + eyeOff * 0.3, dy - h + 15, 5.5, 6, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(cx + 5 + eyeOff * 0.3, dy - h + 15, 5.5, 6, 0, 0, Math.PI * 2);
    ctx.fill();
    // iris
    ctx.fillStyle = p.name === 'Nino' ? '#2C3E50' : '#6C3483';
    ctx.beginPath();
    ctx.arc(cx - 4 + dir * 3, dy - h + 16, 3.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx + 7 + dir * 3, dy - h + 16, 3.5, 0, Math.PI * 2);
    ctx.fill();
    // shine
    ctx.fillStyle = '#FFF';
    ctx.beginPath();
    ctx.arc(cx - 3 + dir * 3, dy - h + 14, 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx + 8 + dir * 3, dy - h + 14, 1.5, 0, Math.PI * 2);
    ctx.fill();

    // --- Mouth ---
    ctx.fillStyle = '#C0392B';
    ctx.beginPath();
    ctx.arc(cx + dir * 1, dy - h + 22, 2, 0, Math.PI);
    ctx.fill();

    // --- Arms ---
    ctx.strokeStyle = '#FDDCB5';
    ctx.lineWidth = 4;
    const armSwing = Math.sin(p.frameTick * 0.3) * (Math.abs(p.vx) > 0.5 ? 11 : 3);
    ctx.beginPath();
    ctx.moveTo(cx - 10, bodyTop + 4);
    ctx.lineTo(cx - 18, bodyTop + 14 + armSwing);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx + 10, bodyTop + 4);
    ctx.lineTo(cx + 18, bodyTop + 14 - armSwing);
    ctx.stroke();

    // --- Legs ---
    ctx.lineWidth = 4.5;
    const legSwing = Math.sin(p.frameTick * 0.3) * (Math.abs(p.vx) > 0.5 ? 8 : 0);
    if (!onGround) {
      // jumping pose - legs tucked
      ctx.beginPath();
      ctx.moveTo(cx - 5, bodyTop + 22);
      ctx.lineTo(cx - 11, bodyTop + 28);
      ctx.lineTo(cx - 5, bodyTop + 34);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(cx + 5, bodyTop + 22);
      ctx.lineTo(cx + 11, bodyTop + 28);
      ctx.lineTo(cx + 5, bodyTop + 34);
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.moveTo(cx - 5, bodyTop + 22);
      ctx.lineTo(cx - 8 + legSwing, dy);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(cx + 5, bodyTop + 22);
      ctx.lineTo(cx + 8 - legSwing, dy);
      ctx.stroke();
    }

    // --- Shoes ---
    ctx.fillStyle = p.name === 'Nino' ? '#E74C3C' : '#AF7AC5';
    if (!onGround) {
      ctx.fillRect(cx - 13, bodyTop + 30, 10, 5);
      ctx.fillRect(cx + 3, bodyTop + 30, 10, 5);
    } else {
      ctx.fillRect(cx - 13 + legSwing, dy - 5, 10, 5);
      ctx.fillRect(cx + 3 - legSwing, dy - 5, 10, 5);
    }

    // --- Name tag ---
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.font = 'bold 12px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(p.name, cx, dy - h - 8);
  }

  function drawStar(s) {
    if (!s.alive) return;
    s.blink += 0.06;
    const glow = 0.7 + Math.sin(s.blink) * 0.3;
    ctx.save();
    ctx.globalAlpha = glow;
    ctx.fillStyle = '#F1C40F';
    ctx.strokeStyle = '#F39C12';
    ctx.lineWidth = 1.5;
    drawStarShape(ctx, s.x, s.y, 5, s.r, s.r / 2);
    ctx.fill();
    ctx.stroke();
    // inner glow
    ctx.fillStyle = '#FEF9E7';
    drawStarShape(ctx, s.x, s.y, 5, s.r * 0.4, s.r * 0.2);
    ctx.fill();
    ctx.restore();
  }

  function drawStarShape(c, cx, cy, spikes, outerR, innerR) {
    let rot = Math.PI / 2 * 3, step = Math.PI / spikes;
    c.beginPath();
    c.moveTo(cx, cy - outerR);
    for (let i = 0; i < spikes; i++) {
      c.lineTo(cx + Math.cos(rot) * outerR, cy + Math.sin(rot) * outerR);
      rot += step;
      c.lineTo(cx + Math.cos(rot) * innerR, cy + Math.sin(rot) * innerR);
      rot += step;
    }
    c.lineTo(cx, cy - outerR);
    c.closePath();
  }

  function drawRoom() {
    // Sky / wall gradient
    const wallGrad = ctx.createLinearGradient(0, 0, 0, FLOOR_Y);
    wallGrad.addColorStop(0, '#D5F5E3');
    wallGrad.addColorStop(1, '#ABEBC6');
    ctx.fillStyle = wallGrad;
    ctx.fillRect(0, 0, W, FLOOR_Y);

    // Wallpaper pattern
    ctx.fillStyle = 'rgba(255,255,255,0.15)';
    for (let yy = 20; yy < FLOOR_Y; yy += 40) {
      for (let xx = 20; xx < W; xx += 40) {
        ctx.beginPath();
        ctx.arc(xx, yy, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Window
    ctx.fillStyle = '#AED6F1';
    ctx.fillRect(390, 35, 120, 100);
    ctx.strokeStyle = '#7FB3D8';
    ctx.lineWidth = 4;
    ctx.strokeRect(390, 35, 120, 100);
    ctx.beginPath();
    ctx.moveTo(450, 35);
    ctx.lineTo(450, 135);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(390, 85);
    ctx.lineTo(510, 85);
    ctx.stroke();
    // curtains
    ctx.fillStyle = '#E8DAEF';
    ctx.fillRect(374, 28, 20, 114);
    ctx.fillRect(506, 28, 20, 114);

    // Poster on wall (left)
    ctx.fillStyle = '#FADBD8';
    ctx.fillRect(180, 55, 70, 85);
    ctx.strokeStyle = '#E6B0AA';
    ctx.lineWidth = 2;
    ctx.strokeRect(180, 55, 70, 85);
    ctx.fillStyle = '#E74C3C';
    ctx.font = 'bold 11px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('POKE', 215, 90);
    ctx.fillText('MON', 215, 108);

    // Clock on wall (right)
    ctx.fillStyle = '#FFF';
    ctx.beginPath();
    ctx.arc(680, 80, 28, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(680, 80);
    ctx.lineTo(680, 58);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(680, 80);
    ctx.lineTo(698, 80);
    ctx.stroke();

    // Floor
    const floorGrad = ctx.createLinearGradient(0, FLOOR_Y, 0, H);
    floorGrad.addColorStop(0, '#A0522D');
    floorGrad.addColorStop(1, '#8B4513');
    ctx.fillStyle = floorGrad;
    ctx.fillRect(0, FLOOR_Y, W, H - FLOOR_Y);

    // Floor planks
    ctx.strokeStyle = 'rgba(0,0,0,0.15)';
    ctx.lineWidth = 1;
    for (let fx = 0; fx < W; fx += 100) {
      ctx.beginPath();
      ctx.moveTo(fx, FLOOR_Y);
      ctx.lineTo(fx, H);
      ctx.stroke();
    }

    // Baseboard
    ctx.fillStyle = '#6B3A2A';
    ctx.fillRect(0, FLOOR_Y - 4, W, 6);

    // Furniture / platforms
    furniture.forEach(f => {
      if (f.type === 'table') {
        ctx.fillStyle = '#D4A574';
        ctx.fillRect(f.x, f.y, f.w, 6);
        // legs
        ctx.fillRect(f.x + 5, f.y + 6, 6, f.h - 6);
        ctx.fillRect(f.x + f.w - 11, f.y + 6, 6, f.h - 6);
      } else if (f.type === 'shelf') {
        ctx.fillStyle = '#C19A6B';
        ctx.fillRect(f.x, f.y, f.w, f.h);
        // bracket
        ctx.fillStyle = '#8B7355';
        ctx.fillRect(f.x + 10, f.y + f.h, 4, 10);
        ctx.fillRect(f.x + f.w - 14, f.y + f.h, 4, 10);
      } else if (f.type === 'platform') {
        ctx.fillStyle = '#C19A6B';
        ctx.fillRect(f.x, f.y, f.w, f.h);
        ctx.strokeStyle = '#A0825A';
        ctx.lineWidth = 1;
        ctx.strokeRect(f.x, f.y, f.w, f.h);
      }
    });
  }

  // --- Collision with platforms ---
  function platformCollision(p) {
    // Floor
    if (p.y >= FLOOR_Y) {
      p.y = FLOOR_Y;
      p.vy = 0;
      p.onGround = true;
    }
    // Platforms / shelves / table top
    furniture.forEach(f => {
      const topY = f.y;
      const prevY = p.y - p.vy;
      if (p.x > f.x - 8 && p.x < f.x + f.w + 8) {
        if (prevY <= topY && p.y >= topY && p.vy >= 0) {
          p.y = topY;
          p.vy = 0;
          p.onGround = true;
        }
      }
    });
    // Walls
    if (p.x < 20) p.x = 20;
    if (p.x > W - 20) p.x = W - 20;
  }

  // --- Star collection ---
  function checkStarCollision(p) {
    stars.forEach(s => {
      if (!s.alive) return;
      const dx = p.x - s.x, dy = (p.y - 25) - s.y;
      if (Math.sqrt(dx * dx + dy * dy) < 28) {
        s.alive = false;
        p.score++;
        document.getElementById(p === P1 ? 'score-p1' : 'score-p2').textContent = p.score;
        document.getElementById('stars-left').textContent = stars.filter(ss => ss.alive).length;
        // Respawn all if none left
        if (stars.every(ss => !ss.alive)) {
          setTimeout(spawnStars, 1000);
        }
      }
    });
  }

  // --- Update ---
  function update() {
    players.forEach(p => {
      const speed = 4.2;
      const jumpForce = -12;

      if (keysDown[p.controls.left]) { p.vx = -speed; p.facing = -1; }
      else if (keysDown[p.controls.right]) { p.vx = speed; p.facing = 1; }
      else { p.vx *= 0.75; }

      if (keysDown[p.controls.jump] && p.onGround) {
        p.vy = jumpForce;
        p.onGround = false;
      }

      p.vy += GRAVITY;
      p.x += p.vx;
      p.y += p.vy;

      p.frameTick++;
      if (Math.abs(p.vx) > 0.5) {
        p.frame = Math.floor(p.frameTick / 8) % 4;
      } else {
        p.frame = 0;
      }

      platformCollision(p);
      checkStarCollision(p);
    });
  }

  // --- Particles ---
  let particles = [];
  function spawnJumpParticles(px, py) {
    for (let i = 0; i < 5; i++) {
      particles.push({
        x: px + (Math.random() - 0.5) * 10,
        y: py,
        vx: (Math.random() - 0.5) * 3,
        vy: -Math.random() * 2,
        life: 20 + Math.random() * 10,
      });
    }
  }

  function updateParticles() {
    particles.forEach(pt => {
      pt.x += pt.vx;
      pt.y += pt.vy;
      pt.vy += 0.1;
      pt.life--;
    });
    particles = particles.filter(pt => pt.life > 0);
  }

  function drawParticles() {
    particles.forEach(pt => {
      ctx.globalAlpha = pt.life / 30;
      ctx.fillStyle = '#D5DBDB';
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 2, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalAlpha = 1;
  }

  // --- Track jumps for particles ---
  let prevOnGround = [true, true];

  // --- Render ---
  function draw() {
    ctx.clearRect(0, 0, W, H);
    drawRoom();
    stars.forEach(drawStar);
    drawParticles();
    // draw players sorted by y so overlap looks right
    const sorted = [...players].sort((a, b) => a.y - b.y);
    sorted.forEach(drawPixelChar);

    // Winner banner
    if (stars.every(s => !s.alive) && (P1.score > 0 || P2.score > 0)) {
      // short flash
    }
  }

  function gameLoop() {
    // Jump particles
    players.forEach((p, i) => {
      if (prevOnGround[i] && !p.onGround) {
        spawnJumpParticles(p.x, p.y);
      }
      prevOnGround[i] = p.onGround;
    });

    update();
    updateParticles();
    draw();
    requestAnimationFrame(gameLoop);
  }

  function resetGame() {
    P1.x = 140; P1.y = FLOOR_Y; P1.vx = 0; P1.vy = 0; P1.score = 0; P1.onGround = true;
    P2.x = 720; P2.y = FLOOR_Y; P2.vx = 0; P2.vy = 0; P2.score = 0; P2.onGround = true;
    document.getElementById('score-p1').textContent = '0';
    document.getElementById('score-p2').textContent = '0';
    spawnStars();
  }

  spawnStars();
  gameLoop();

  // Focus canvas area so keys work
  canvas.setAttribute('tabindex', '0');
  canvas.focus();
})();
</script>
""")
