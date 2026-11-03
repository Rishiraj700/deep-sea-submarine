/**
 * Abyssal Expedition: Deep Sea Submarine
 * Multimedia Systems Lab — Lab Test 2
 * Full HTML5 Canvas + Web Audio API Implementation for Vercel Deployment.
 */

// ================= CONSTANTS & CONFIG =================
const CANVAS_WIDTH = 960;
const CANVAS_HEIGHT = 640;

const STATE_START = "start";
const STATE_PLAYING = "playing";
const STATE_PAUSED = "paused";
const STATE_GAME_OVER = "game_over";

const ZONE_SUNLIGHT_MAX = 250;
const ZONE_TWILIGHT_MAX = 600;

const SUB_ACCEL = 0.55;
const SUB_MAX_SPEED = 5.2;
const SUB_BOOST_SPEED = 8.0;
const SUB_DRAG = 0.92;
const SUB_BUOYANCY = -0.06;

const MAX_HULL = 100;
const MAX_OXYGEN = 100;
const OXYGEN_DEPLETION_RATE = 2.2;
const OXYGEN_BOOST_COST = 5.0;
const SONAR_COOLDOWN = 4.0;
const COMBO_TIMEOUT = 3.2;

const SCORE_PEARL = 100;
const SCORE_CLAM = 350;
const SCORE_SHIELD_PICKUP = 200;
const MAX_COMBO = 4;

// ================= PROCEDURAL WEB AUDIO SYNTHESIZER =================
class SoundController {
  constructor() {
    this.ctx = null;
    this.muted = false;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    }
    if (this.ctx.state === "suspended") {
      this.ctx.resume();
    }
  }

  toggleMute() {
    this.muted = !this.muted;
    return this.muted;
  }

  playSonarPing() {
    if (this.muted || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(950, now);
    osc.frequency.exponentialRampToValueAtTime(860, now + 1.2);

    gain.gain.setValueAtTime(0.35, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.2);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 1.2);
  }

  playPearlCollect() {
    if (this.muted || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(600, now);
    osc.frequency.exponentialRampToValueAtTime(1400, now + 0.3);

    gain.gain.setValueAtTime(0.28, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.3);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.3);
  }

  playClamBonus() {
    if (this.muted || !this.ctx) return;
    const notes = [1046.5, 1318.5, 1567.9, 2093.0]; // C6, E6, G6, C7
    const now = this.ctx.currentTime;

    notes.forEach((freq, idx) => {
      const startTime = now + idx * 0.08;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq, startTime);

      gain.gain.setValueAtTime(0.3, startTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.35);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(startTime);
      osc.stop(startTime + 0.35);
    });
  }

  playExplosion() {
    if (this.muted || !this.ctx) return;
    const now = this.ctx.currentTime;
    const bufferSize = this.ctx.sampleRate * 0.6;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = buffer.getChannelData(0);

    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(180, now);
    filter.frequency.exponentialRampToValueAtTime(40, now + 0.6);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.6, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);

    whiteNoise.connect(filter);
    filter.connect(gain);
    gain.connect(this.ctx.destination);

    whiteNoise.start(now);
  }

  playShieldDeflect() {
    if (this.muted || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(880, now);
    osc.frequency.exponentialRampToValueAtTime(220, now + 0.35);

    gain.gain.setValueAtTime(0.35, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.35);
  }

  playAlarm() {
    if (this.muted || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(480, now);
    osc.frequency.setValueAtTime(640, now + 0.15);

    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.35);
  }
}

// ================= PARTICLE SYSTEMS =================
class Bubble {
  constructor(x, y, isPropeller = false, isBoost = false) {
    this.x = x;
    this.y = y;
    this.isPropeller = isPropeller;
    this.isBoost = isBoost;

    if (isBoost) {
      this.radius = 3.5 + Math.random() * 3.5;
      this.vy = -1.5 - Math.random() * 2.0;
      this.vx = -4.5 - Math.random() * 2.5;
      this.maxLife = 0.6 + Math.random() * 0.6;
    } else if (isPropeller) {
      this.radius = 2.0 + Math.random() * 2.5;
      this.vy = -0.8 - Math.random() * 1.4;
      this.vx = -2.2 - Math.random() * 1.5;
      this.maxLife = 0.8 + Math.random() * 0.8;
    } else {
      this.radius = 1.5 + Math.random() * 3.5;
      this.vy = -0.6 - Math.random() * 1.2;
      this.vx = (Math.random() - 0.5) * 0.6;
      this.maxLife = 4.0 + Math.random() * 4.0;
    }

    this.life = this.maxLife;
    this.phase = Math.random() * Math.PI * 2;
  }

  update(dt) {
    this.life -= dt;
    this.y += this.vy * (60 * dt);
    this.phase += 3.0 * dt;
    this.x += (this.vx + Math.sin(this.phase) * 0.4) * (60 * dt);
    return this.life > 0 && this.y > -20;
  }

  draw(ctx) {
    const alpha = Math.min(1.0, this.life / (this.maxLife * 0.3)) * 0.8;
    ctx.save();
    ctx.strokeStyle = `rgba(180, 235, 255, ${alpha})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.stroke();

    if (this.radius >= 3) {
      ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.7})`;
      ctx.beginPath();
      ctx.arc(this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.3, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }
}

class Sparkle {
  constructor(x, y, color = "#ffd700") {
    this.x = x;
    this.y = y;
    const angle = Math.random() * Math.PI * 2;
    const speed = 1.5 + Math.random() * 3.5;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed;
    this.color = color;
    this.maxLife = 0.4 + Math.random() * 0.4;
    this.life = this.maxLife;
    this.size = 2.5 + Math.random() * 2.5;
  }

  update(dt) {
    this.life -= dt;
    this.x += this.vx * (60 * dt);
    this.y += this.vy * (60 * dt);
    this.vx *= 0.94;
    this.vy *= 0.94;
    return this.life > 0;
  }

  draw(ctx) {
    const alpha = this.life / this.maxLife;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

class SonarWave {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.radius = 10;
    this.maxRadius = 420;
    this.speed = 380;
    this.active = true;
  }

  update(dt) {
    this.radius += this.speed * dt;
    if (this.radius >= this.maxRadius) this.active = false;
    return this.active;
  }

  draw(ctx) {
    const ratio = this.radius / this.maxRadius;
    const alpha = (1 - ratio) * 0.8;
    ctx.save();
    ctx.strokeStyle = `rgba(70, 230, 255, ${alpha})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.stroke();

    if (this.radius > 25) {
      ctx.strokeStyle = `rgba(50, 190, 230, ${alpha * 0.45})`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius - 12, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();
  }
}

// ================= GAME ENTITIES =================
class Pearl {
  constructor(x, y) {
    this.x = x;
    this.baseY = y;
    this.y = y;
    this.radius = 14;
    this.speedX = 1.6 + Math.random() * 0.9;
    this.phase = Math.random() * Math.PI * 2;
    this.frequency = 2.0 + Math.random() * 1.0;
    this.amplitude = 18 + Math.random() * 14;
    this.alive = true;
    this.isMagnetized = false;
  }

  update(dt, player) {
    this.phase += this.frequency * dt;
    if (this.isMagnetized && player && player.alive) {
      const dx = player.x - this.x;
      const dy = player.y - this.y;
      const dist = Math.hypot(dx, dy);
      if (dist > 5) {
        const pull = 320 * dt;
        this.x += (dx / dist) * pull;
        this.y += (dy / dist) * pull;
      }
    } else {
      this.x -= this.speedX * (60 * dt);
      this.y = this.baseY + Math.sin(this.phase) * this.amplitude;
    }
    if (this.x < -60) this.alive = false;
  }

  draw(ctx) {
    ctx.save();
    // Halo glow
    const grad = ctx.createRadialGradient(this.x, this.y, 4, this.x, this.y, 18);
    grad.addColorStop(0, "rgba(220, 245, 255, 0.9)");
    grad.addColorStop(0.5, "rgba(80, 220, 255, 0.4)");
    grad.addColorStop(1, "rgba(80, 220, 255, 0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(this.x, this.y, 18, 0, Math.PI * 2);
    ctx.fill();

    // Pearl Core
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(this.x, this.y, 7, 0, Math.PI * 2);
    ctx.fill();

    // Specular shine
    ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
    ctx.beginPath();
    ctx.arc(this.x - 2, this.y - 2, 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

class GoldenClam {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.radius = 18;
    this.speedX = 1.4;
    this.phase = Math.random() * Math.PI * 2;
    this.alive = true;
  }

  update(dt) {
    this.phase += 2.0 * dt;
    this.x -= this.speedX * (60 * dt);
    this.y += Math.sin(this.phase) * 0.4 * (60 * dt);
    if (this.x < -60) this.alive = false;
  }

  draw(ctx) {
    ctx.save();
    // Golden Glow
    const grad = ctx.createRadialGradient(this.x, this.y, 6, this.x, this.y, 24);
    grad.addColorStop(0, "rgba(255, 215, 0, 0.8)");
    grad.addColorStop(1, "rgba(255, 215, 0, 0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(this.x, this.y, 24, 0, Math.PI * 2);
    ctx.fill();

    // Clam Shell
    ctx.fillStyle = "#ffd700";
    ctx.beginPath();
    ctx.arc(this.x, this.y, 14, Math.PI, 0, false);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = "#b8860b";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Clam Pearl inside
    ctx.fillStyle = "#fffff0";
    ctx.beginPath();
    ctx.arc(this.x, this.y - 2, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

class ShieldPickup {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.radius = 18;
    this.speedX = 1.6;
    this.phase = Math.random() * Math.PI * 2;
    this.alive = true;
  }

  update(dt) {
    this.phase += 2.5 * dt;
    this.x -= this.speedX * (60 * dt);
    this.y += Math.sin(this.phase) * 0.6 * (60 * dt);
    if (this.x < -60) this.alive = false;
  }

  draw(ctx) {
    ctx.save();
    ctx.strokeStyle = "#50e0ff";
    ctx.lineWidth = 2;
    ctx.fillStyle = "rgba(40, 180, 255, 0.4)";
    ctx.beginPath();
    ctx.arc(this.x, this.y, 14, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Crest inside
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(this.x, this.y, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

class DepthCharge {
  constructor(x, y, speedY) {
    this.baseX = x;
    this.x = x;
    this.y = y;
    this.radius = 18;
    this.speedY = speedY || 1.6;
    this.swingPhase = Math.random() * Math.PI * 2;
    this.swingSpeed = 1.8;
    this.swingAmp = 35;
    this.alive = true;
    this.blinkTimer = 0;
    this.isBlinking = false;
  }

  update(dt, player) {
    this.swingPhase += this.swingSpeed * dt;
    this.y += this.speedY * (60 * dt);
    this.x = this.baseX + Math.sin(this.swingPhase) * this.swingAmp;

    let dist = 9999;
    if (player && player.alive) {
      dist = Math.hypot(player.x - this.x, player.y - this.y);
    }
    const blinkPeriod = dist < 160 ? 0.15 : 0.5;
    this.blinkTimer += dt;
    if (this.blinkTimer >= blinkPeriod) {
      this.blinkTimer = 0;
      this.isBlinking = !this.isBlinking;
    }

    if (this.y > CANVAS_HEIGHT + 60) this.alive = false;
  }

  draw(ctx) {
    ctx.save();
    // Mine Spikes
    ctx.strokeStyle = "#404550";
    ctx.lineWidth = 3;
    for (let i = 0; i < 8; i++) {
      const angle = (Math.PI * 2 / 8) * i;
      const sx = this.x + Math.cos(angle) * 19;
      const sy = this.y + Math.sin(angle) * 19;
      ctx.beginPath();
      ctx.moveTo(this.x, this.y);
      ctx.lineTo(sx, sy);
      ctx.stroke();
    }

    // Sphere Body
    ctx.fillStyle = "#1e232a";
    ctx.beginPath();
    ctx.arc(this.x, this.y, 13, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#505865";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Red Proximity Beacon
    if (this.isBlinking) {
      ctx.fillStyle = "#ff2020";
      ctx.beginPath();
      ctx.arc(this.x, this.y, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#ffcccc";
      ctx.beginPath();
      ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
      ctx.fill();
    } else {
      ctx.fillStyle = "#701010";
      ctx.beginPath();
      ctx.arc(this.x, this.y, 4, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }
}

class Torpedo {
  constructor(x, y, speedX) {
    this.x = x;
    this.y = y;
    this.radius = 12;
    this.speedX = speedX || 6.8;
    this.alive = true;
    this.bubbleTimer = 0;
  }

  update(dt, bubbles) {
    this.x -= this.speedX * (60 * dt);
    this.bubbleTimer += dt;
    if (this.bubbleTimer >= 0.04) {
      this.bubbleTimer = 0;
      bubbles.push(new Bubble(this.x + 24, this.y, true, false));
    }
    if (this.x < -80) this.alive = false;
  }

  draw(ctx) {
    ctx.save();
    // Torpedo Body
    ctx.fillStyle = "#333842";
    ctx.fillRect(this.x - 20, this.y - 6, 34, 12);

    // Hazard Stripes
    ctx.fillStyle = "#ffd700";
    for (let ox of [-8, 0, 8]) {
      ctx.fillRect(this.x + ox, this.y - 6, 3, 12);
    }

    // Warhead Red Nose
    ctx.fillStyle = "#e03030";
    ctx.beginPath();
    ctx.arc(this.x - 18, this.y, 6, Math.PI * 0.5, Math.PI * 1.5, false);
    ctx.fill();

    // Propeller Fin
    ctx.fillStyle = "#a09040";
    ctx.fillRect(this.x + 14, this.y - 8, 4, 16);
    ctx.restore();
  }
}

// ================= SUBMARINE PLAYER =================
class Submarine {
  constructor(x = 140, y = 300) {
    this.x = x;
    this.y = y;
    this.vx = 0;
    this.vy = 0;
    this.radius = 24;
    this.hull = MAX_HULL;
    this.oxygen = MAX_OXYGEN;
    this.hasShield = false;
    this.alive = true;
    this.sonarTimer = SONAR_COOLDOWN;
    this.isBoosting = false;
    this.invulnerableTimer = 0;
    this.pitchAngle = 0;
    this.bubbleTimer = 0;
    this.propellerAngle = 0;
    this.timer = 0;
  }

  reset(x = 140, y = 300) {
    this.x = x;
    this.y = y;
    this.vx = 0;
    this.vy = 0;
    this.hull = MAX_HULL;
    this.oxygen = MAX_OXYGEN;
    this.hasShield = false;
    this.alive = true;
    this.sonarTimer = SONAR_COOLDOWN;
    this.isBoosting = false;
    this.invulnerableTimer = 0;
    this.pitchAngle = 0;
  }

  update(dt, input, soundCtrl, bubbles, sonarWaves) {
    if (!this.alive) return;
    this.timer += dt;
    this.sonarTimer += dt;
    if (this.invulnerableTimer > 0) {
      this.invulnerableTimer = Math.max(0, this.invulnerableTimer - dt);
    }

    // Oxygen depletion
    let oxyDrain = OXYGEN_DEPLETION_RATE * dt;
    if (this.isBoosting) oxyDrain += OXYGEN_BOOST_COST * dt;
    this.oxygen = Math.max(0, this.oxygen - oxyDrain);
    if (this.oxygen <= 0) {
      this.alive = false;
      soundCtrl.playAlarm();
    }

    // Input thrust
    let ax = 0, ay = 0;
    if (input.left) ax -= SUB_ACCEL;
    if (input.right) ax += SUB_ACCEL;
    if (input.up) ay -= SUB_ACCEL;
    if (input.down) ay += SUB_ACCEL;

    this.isBoosting = input.boost && this.oxygen > 5;
    const accelMult = this.isBoosting ? 1.5 : 1.0;
    const speedLimit = this.isBoosting ? SUB_BOOST_SPEED : SUB_MAX_SPEED;

    this.vx += ax * accelMult;
    this.vy += (ay * accelMult) + SUB_BUOYANCY;

    this.vx *= SUB_DRAG;
    this.vy *= SUB_DRAG;

    const currSpeed = Math.hypot(this.vx, this.vy);
    if (currSpeed > speedLimit) {
      const scale = speedLimit / currSpeed;
      this.vx *= scale;
      this.vy *= scale;
    }

    this.x += this.vx * (60 * dt);
    this.y += this.vy * (60 * dt);

    this.x = Math.max(50, Math.min(CANVAS_WIDTH - 60, this.x));
    this.y = Math.max(50, Math.min(CANVAS_HEIGHT - 55, this.y));

    // Pitch tilt
    const targetPitch = Math.max(-16, Math.min(16, -this.vy * 3.8));
    this.pitchAngle += (targetPitch - this.pitchAngle) * 0.15;

    // Propeller bubbles
    this.bubbleTimer += dt;
    const bubbleThreshold = this.isBoosting ? 0.04 : 0.12;
    if (this.bubbleTimer >= bubbleThreshold) {
      this.bubbleTimer = 0;
      const rad = (this.pitchAngle * Math.PI) / 180;
      const tailX = this.x - Math.cos(rad) * 42;
      const tailY = this.y + Math.sin(rad) * 42;
      bubbles.push(new Bubble(tailX, tailY, true, this.isBoosting));
    }
  }

  triggerSonar(soundCtrl, sonarWaves) {
    if (this.sonarTimer >= SONAR_COOLDOWN && this.alive) {
      this.sonarTimer = 0;
      sonarWaves.push(new SonarWave(this.x, this.y));
      soundCtrl.playSonarPing();
      return true;
    }
    return false;
  }

  takeDamage(amount, soundCtrl, sparkles) {
    if (!this.alive || this.invulnerableTimer > 0) return false;

    if (this.hasShield) {
      this.hasShield = false;
      this.invulnerableTimer = 0.8;
      soundCtrl.playShieldDeflect();
      for (let i = 0; i < 18; i++) {
        sparkles.push(new Sparkle(this.x, this.y, "#50e0ff"));
      }
      return "shield_absorbed";
    } else {
      this.hull = Math.max(0, this.hull - amount);
      this.invulnerableTimer = 1.4;
      soundCtrl.playExplosion();
      for (let i = 0; i < 24; i++) {
        sparkles.push(new Sparkle(this.x, this.y, "#ff6030"));
      }
      if (this.hull <= 0) this.alive = false;
      return "damaged";
    }
  }

  drawHeadlight(ctx) {
    const rad = (this.pitchAngle * Math.PI) / 180;
    const bowX = this.x + Math.cos(rad) * 40;
    const bowY = this.y - Math.sin(rad) * 40;
    const beamLength = 260;
    const beamSpread = 70;

    const endX = bowX + Math.cos(rad) * beamLength;
    const endY = bowY - Math.sin(rad) * beamLength;

    const perpX = -Math.sin(rad);
    const perpY = -Math.cos(rad);

    ctx.save();
    const grad = ctx.createRadialGradient(bowX, bowY, 10, endX, endY, beamLength);
    grad.addColorStop(0, "rgba(255, 255, 210, 0.45)");
    grad.addColorStop(0.5, "rgba(255, 255, 190, 0.2)");
    grad.addColorStop(1, "rgba(255, 255, 180, 0)");

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.moveTo(bowX, bowY);
    ctx.lineTo(endX + perpX * beamSpread, endY + perpY * beamSpread);
    ctx.lineTo(endX - perpX * beamSpread, endY - perpY * beamSpread);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  draw(ctx) {
    if (!this.alive) return;
    this.drawHeadlight(ctx);

    if (this.invulnerableTimer > 0 && Math.floor(this.invulnerableTimer * 16) % 2 === 0) {
      return;
    }

    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate((this.pitchAngle * Math.PI) / 180);

    // Submarine Hull
    ctx.fillStyle = "#1c4e80";
    ctx.beginPath();
    ctx.ellipse(0, 0, 42, 20, 0, 0, Math.PI * 2);
    ctx.fill();

    // Upper highlight
    ctx.fillStyle = "#2d78be";
    ctx.beginPath();
    ctx.ellipse(2, -4, 34, 10, 0, 0, Math.PI * 2);
    ctx.fill();

    // Conning Tower
    ctx.fillStyle = "#235f96";
    ctx.fillRect(-6, -24, 16, 12);
    ctx.strokeStyle = "#14375a";
    ctx.lineWidth = 2;
    ctx.strokeRect(-6, -24, 16, 12);

    // Periscope
    ctx.strokeStyle = "#b4c3d2";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(2, -24);
    ctx.lineTo(2, -30);
    ctx.lineTo(8, -30);
    ctx.stroke();

    // Portholes
    for (let px of [-14, 0, 14]) {
      ctx.fillStyle = "#d4af37"; // Brass rim
      ctx.beginPath();
      ctx.arc(px, 0, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#5af0ff"; // Glowing glass
      ctx.beginPath();
      ctx.arc(px, 0, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    // Stern Propeller
    ctx.fillStyle = "#e6be3c";
    ctx.fillRect(-44, -10, 4, 20);

    // Shield Aura
    if (this.hasShield) {
      const pulse = 1.0 + 0.06 * Math.sin(this.timer * 7.0);
      ctx.strokeStyle = "rgba(80, 220, 255, 0.75)";
      ctx.lineWidth = 3;
      ctx.fillStyle = "rgba(60, 190, 255, 0.2)";
      ctx.beginPath();
      ctx.ellipse(0, 0, 48 * pulse, 28 * pulse, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }

    ctx.restore();
  }
}

// ================= MASTER GAME CONTROLLER =================
class Game {
  constructor() {
    this.canvas = document.getElementById("gameCanvas");
    this.ctx = this.canvas.getContext("2d");
    this.soundCtrl = new SoundController();

    this.state = STATE_START;
    this.score = 0;
    this.highScore = parseInt(localStorage.getItem("abyssal_high_score") || "0", 10);
    this.depth = 50;
    this.combo = 1;
    this.comboTimer = 0;
    this.maxComboStreak = 1;
    this.pearlsCollected = 0;
    this.clamsCollected = 0;
    this.gameOverReason = "";

    this.player = new Submarine();
    this.collectibles = [];
    this.hazards = [];
    this.bubbles = [];
    this.sparkles = [];
    this.sonarWaves = [];
    this.torpedoWarnings = [];

    this.spawnTimers = { pearl: 0, clam: 0, shield: 0, mine: 0, torpedo: 0 };
    this.input = { up: false, down: false, left: false, right: false, boost: false };
    this.lastTime = performance.now();

    // Seabed kelp fronds
    this.kelp = [];
    for (let x = 40; x < CANVAS_WIDTH + 80; x += 55) {
      this.kelp.push({
        baseX: x,
        height: 90 + Math.random() * 70,
        phase: Math.random() * Math.PI * 2,
        speed: 1.2 + Math.random() * 1.0,
      });
    }

    // Seed ambient bubbles
    for (let i = 0; i < 35; i++) {
      this.bubbles.push(new Bubble(Math.random() * CANVAS_WIDTH, Math.random() * CANVAS_HEIGHT));
    }

    this.bindEvents();
    this.loop = this.loop.bind(this);
    requestAnimationFrame(this.loop);
  }

  resetGame() {
    this.player.reset();
    this.collectibles = [];
    this.hazards = [];
    this.sonarWaves = [];
    this.torpedoWarnings = [];
    this.score = 0;
    this.depth = 50;
    this.combo = 1;
    this.comboTimer = 0;
    this.maxComboStreak = 1;
    this.pearlsCollected = 0;
    this.clamsCollected = 0;
    this.state = STATE_PLAYING;
  }

  bindEvents() {
    window.addEventListener("keydown", (e) => {
      this.soundCtrl.init();
      if (e.code === "KeyW" || e.code === "ArrowUp") this.input.up = true;
      if (e.code === "KeyS" || e.code === "ArrowDown") this.input.down = true;
      if (e.code === "KeyA" || e.code === "ArrowLeft") this.input.left = true;
      if (e.code === "KeyD" || e.code === "ArrowRight") this.input.right = true;
      if (e.code === "ShiftLeft" || e.code === "ShiftRight" || e.code === "KeyB") this.input.boost = true;

      if (e.code === "Space") {
        e.preventDefault();
        if (this.state === STATE_START) this.resetGame();
        else if (this.state === STATE_PLAYING) this.player.triggerSonar(this.soundCtrl, this.sonarWaves);
        else if (this.state === STATE_GAME_OVER) this.resetGame();
      }

      if (e.code === "Enter" && this.state === STATE_START) this.resetGame();
      if (e.code === "KeyP" || e.code === "Escape") {
        if (this.state === STATE_PLAYING) this.state = STATE_PAUSED;
        else if (this.state === STATE_PAUSED) this.state = STATE_PLAYING;
      }
      if (e.code === "KeyR") this.resetGame();
      if (e.code === "KeyM") this.soundCtrl.toggleMute();
    });

    window.addEventListener("keyup", (e) => {
      if (e.code === "KeyW" || e.code === "ArrowUp") this.input.up = false;
      if (e.code === "KeyS" || e.code === "ArrowDown") this.input.down = false;
      if (e.code === "KeyA" || e.code === "ArrowLeft") this.input.left = false;
      if (e.code === "KeyD" || e.code === "ArrowRight") this.input.right = false;
      if (e.code === "ShiftLeft" || e.code === "ShiftRight" || e.code === "KeyB") this.input.boost = false;
    });

    // Mobile / Touch controls
    const bindTouch = (id, prop) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("touchstart", (e) => { e.preventDefault(); this.soundCtrl.init(); this.input[prop] = true; });
      el.addEventListener("touchend", (e) => { e.preventDefault(); this.input[prop] = false; });
    };

    bindTouch("btn-up", "up");
    bindTouch("btn-down", "down");
    bindTouch("btn-left", "left");
    bindTouch("btn-right", "right");
    bindTouch("btn-boost", "boost");

    const sonarBtn = document.getElementById("btn-sonar");
    if (sonarBtn) {
      sonarBtn.addEventListener("touchstart", (e) => {
        e.preventDefault();
        this.soundCtrl.init();
        if (this.state === STATE_START) this.resetGame();
        else if (this.state === STATE_PLAYING) this.player.triggerSonar(this.soundCtrl, this.sonarWaves);
        else if (this.state === STATE_GAME_OVER) this.resetGame();
      });
    }

    this.canvas.addEventListener("click", () => {
      this.soundCtrl.init();
      if (this.state === STATE_START || this.state === STATE_GAME_OVER) this.resetGame();
    });
  }

  update(dt) {
    if (this.state === STATE_PLAYING) {
      this.player.update(dt, this.input, this.soundCtrl, this.bubbles, this.sonarWaves);

      if (!this.player.alive && this.player.oxygen <= 0) {
        this.triggerGameOver("oxygen");
        return;
      }

      // Depth accumulation
      const vertRate = Math.max(0.5, 3.5 + this.player.vy * 0.8);
      this.depth += vertRate * dt;
      this.score += Math.floor(vertRate * dt * 5);

      // Combo decay
      if (this.combo > 1) {
        this.comboTimer -= dt;
        if (this.comboTimer <= 0) {
          this.combo = 1;
          this.comboTimer = 0;
        }
      }

      // Spawning
      const depthFactor = Math.min(2.5, 1.0 + (this.depth / 500.0));
      this.spawnTimers.pearl += dt;
      if (this.spawnTimers.pearl >= Math.max(0.9, 1.6 / depthFactor)) {
        this.spawnTimers.pearl = 0;
        this.collectibles.push(new Pearl(CANVAS_WIDTH + 40, 60 + Math.random() * (CANVAS_HEIGHT - 120)));
      }

      this.spawnTimers.clam += dt;
      if (this.spawnTimers.clam >= 18.0) {
        this.spawnTimers.clam = 0;
        this.collectibles.push(new GoldenClam(CANVAS_WIDTH + 40, CANVAS_HEIGHT * 0.5 + Math.random() * 200));
      }

      this.spawnTimers.shield += dt;
      if (this.spawnTimers.shield >= 28.0) {
        this.spawnTimers.shield = 0;
        this.collectibles.push(new ShieldPickup(CANVAS_WIDTH + 40, 80 + Math.random() * (CANVAS_HEIGHT - 160)));
      }

      this.spawnTimers.mine += dt;
      if (this.spawnTimers.mine >= Math.max(1.4, 3.8 / depthFactor)) {
        this.spawnTimers.mine = 0;
        this.hazards.push(new DepthCharge(120 + Math.random() * (CANVAS_WIDTH - 200), -50, (1.2 + Math.random()) * (1 + 0.3 * (this.depth / 1000))));
      }

      if (this.depth > 150) {
        this.spawnTimers.torpedo += dt;
        if (this.spawnTimers.torpedo >= Math.max(2.8, 7.5 / depthFactor)) {
          this.spawnTimers.torpedo = 0;
          this.hazards.push(new Torpedo(CANVAS_WIDTH + 40, 80 + Math.random() * (CANVAS_HEIGHT - 160), (5.8 + Math.random() * 2.5) * (1 + 0.25 * (this.depth / 1000))));
        }
      }

      // Collisions
      this.handleCollisions();
    }

    // Entity updates
    this.collectibles.forEach(c => c.update(dt, this.player));
    this.collectibles = this.collectibles.filter(c => c.alive);

    this.hazards.forEach(h => {
      if (h instanceof Torpedo) h.update(dt, this.bubbles);
      else h.update(dt, this.player);
    });
    this.hazards = this.hazards.filter(h => h.alive);

    this.bubbles = this.bubbles.filter(b => b.update(dt));
    this.sparkles = this.sparkles.filter(s => s.update(dt));
    this.sonarWaves = this.sonarWaves.filter(sw => sw.update(dt));

    if (this.bubbles.length < 35 && Math.random() < 0.25) {
      this.bubbles.push(new Bubble(Math.random() * CANVAS_WIDTH, CANVAS_HEIGHT + 10));
    }
  }

  handleCollisions() {
    if (!this.player.alive) return;

    // Collectibles
    for (let item of this.collectibles) {
      if (!item.alive) continue;
      const distSq = (this.player.x - item.x) ** 2 + (this.player.y - item.y) ** 2;
      const radii = this.player.radius + item.radius;
      if (distSq <= radii * radii) {
        item.alive = false;
        if (item instanceof Pearl) {
          this.pearlsCollected++;
          this.score += SCORE_PEARL * this.combo;
          this.soundCtrl.playPearlCollect();
          this.combo = Math.min(MAX_COMBO, this.combo + 1);
          this.maxComboStreak = Math.max(this.maxComboStreak, this.combo);
          this.comboTimer = COMBO_TIMEOUT;
          for (let i = 0; i < 12; i++) this.sparkles.push(new Sparkle(item.x, item.y, "#50e0ff"));
        } else if (item instanceof GoldenClam) {
          this.clamsCollected++;
          this.score += SCORE_CLAM * this.combo;
          this.player.oxygen = Math.min(MAX_OXYGEN, this.player.oxygen + 25);
          this.soundCtrl.playClamBonus();
          for (let i = 0; i < 20; i++) this.sparkles.push(new Sparkle(item.x, item.y, "#ffd700"));
        } else if (item instanceof ShieldPickup) {
          this.player.hasShield = true;
          this.score += SCORE_SHIELD_PICKUP;
          this.soundCtrl.playShieldDeflect();
        }
      }
    }

    // Hazards
    for (let hazard of this.hazards) {
      if (!hazard.alive) continue;
      const distSq = (this.player.x - hazard.x) ** 2 + (this.player.y - hazard.y) ** 2;
      const radii = this.player.radius + hazard.radius;
      if (distSq <= radii * radii) {
        hazard.alive = false;
        const dmg = hazard instanceof Torpedo ? 45 : 35;
        const res = this.player.takeDamage(dmg, this.soundCtrl, this.sparkles);
        if (res === "damaged") {
          this.combo = 1;
          this.comboTimer = 0;
          if (!this.player.alive) this.triggerGameOver("hull");
        }
      }
    }

    // Sonar attraction
    for (let wave of this.sonarWaves) {
      for (let c of this.collectibles) {
        if (c instanceof Pearl) {
          const dist = Math.hypot(c.x - wave.x, c.y - wave.y);
          if (Math.abs(dist - wave.radius) < 35) c.isMagnetized = true;
        }
      }
    }
  }

  triggerGameOver(reason) {
    this.state = STATE_GAME_OVER;
    this.gameOverReason = reason;
    if (this.score > this.highScore) {
      this.highScore = this.score;
      localStorage.setItem("abyssal_high_score", this.highScore.toString());
    }
  }

  draw() {
    this.ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // Dynamic depth background
    const t = Math.min(1.0, this.depth / 800.0);
    const grad = this.ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT);
    if (this.depth < ZONE_SUNLIGHT_MAX) {
      grad.addColorStop(0, "#0c2d50");
      grad.addColorStop(1, "#061934");
    } else if (this.depth < ZONE_TWILIGHT_MAX) {
      grad.addColorStop(0, "#061934");
      grad.addColorStop(1, "#020a18");
    } else {
      grad.addColorStop(0, "#020a18");
      grad.addColorStop(1, "#01040c");
    }
    this.ctx.fillStyle = grad;
    this.ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // Sun caustics (in shallow water)
    if (this.depth < ZONE_TWILIGHT_MAX) {
      const now = performance.now() * 0.001;
      this.ctx.save();
      for (let r = 0; r < 5; r++) {
        const rx = 100 + r * 180 + Math.sin(now + r) * 40;
        this.ctx.fillStyle = "rgba(180, 240, 255, 0.035)";
        this.ctx.beginPath();
        this.ctx.moveTo(rx - 20, 0);
        this.ctx.lineTo(rx + 30, 0);
        this.ctx.lineTo(rx + 160, CANVAS_HEIGHT);
        this.ctx.lineTo(rx + 60, CANVAS_HEIGHT);
        this.ctx.closePath();
        this.ctx.fill();
      }
      this.ctx.restore();
    }

    // Swaying Kelp on Seabed
    const kelpTime = performance.now() * 0.001;
    this.ctx.save();
    for (let k of this.kelp) {
      this.ctx.strokeStyle = "#14482d";
      this.ctx.lineWidth = 4;
      this.ctx.beginPath();
      this.ctx.moveTo(k.baseX, CANVAS_HEIGHT);
      const sway = Math.sin(kelpTime * k.speed + k.phase) * 16;
      this.ctx.quadraticCurveTo(k.baseX + sway * 0.5, CANVAS_HEIGHT - k.height * 0.5, k.baseX + sway, CANVAS_HEIGHT - k.height);
      this.ctx.stroke();
    }
    this.ctx.restore();

    // Entities & Particles
    this.sonarWaves.forEach(sw => sw.draw(this.ctx));
    this.collectibles.forEach(c => c.draw(this.ctx));
    this.hazards.forEach(h => h.draw(this.ctx));
    this.player.draw(this.ctx);
    this.bubbles.forEach(b => b.draw(this.ctx));
    this.sparkles.forEach(s => s.draw(this.ctx));

    // UI State Rendering
    if (this.state === STATE_PLAYING) {
      this.drawHUD();
    } else if (this.state === STATE_START) {
      this.drawStartScreen();
    } else if (this.state === STATE_PAUSED) {
      this.drawHUD();
      this.drawPauseScreen();
    } else if (this.state === STATE_GAME_OVER) {
      this.drawGameOverScreen();
    }
  }

  drawHUD() {
    const ctx = this.ctx;
    ctx.save();
    ctx.font = "bold 14px 'Share Tech Mono', monospace";

    // Hull Bar
    ctx.fillStyle = "#141923";
    ctx.fillRect(18, 14, 160, 16);
    const hullRatio = Math.max(0, this.player.hull / MAX_HULL);
    ctx.fillStyle = hullRatio > 0.5 ? "#3ce678" : (hullRatio > 0.25 ? "#ffe63c" : "#ff3c3c");
    ctx.fillRect(18, 14, 160 * hullRatio, 16);
    ctx.strokeStyle = "#506e8c";
    ctx.strokeRect(18, 14, 160, 16);
    ctx.fillStyle = "#ffffff";
    ctx.fillText(`HULL: ${Math.round(this.player.hull)}%`, 18, 44);

    // Oxygen Bar
    ctx.fillStyle = "#141923";
    ctx.fillRect(18, 52, 160, 16);
    const oxyRatio = Math.max(0, this.player.oxygen / MAX_OXYGEN);
    ctx.fillStyle = oxyRatio > 0.35 ? "#50e6ff" : (oxyRatio > 0.18 ? "#ff8c28" : "#ff3c3c");
    ctx.fillRect(18, 52, 160 * oxyRatio, 16);
    ctx.strokeStyle = "#506e8c";
    ctx.strokeRect(18, 52, 160, 16);
    ctx.fillStyle = "#ffffff";
    ctx.fillText(`OXYGEN: ${Math.round(this.player.oxygen)}%`, 18, 82);

    // Depth & Zone
    ctx.textAlign = "center";
    ctx.font = "bold 18px 'Share Tech Mono', monospace";
    ctx.fillText(`DEPTH: ${Math.round(this.depth)} m`, CANVAS_WIDTH / 2, 26);
    ctx.font = "14px 'Share Tech Mono', monospace";
    let zone = "[SUNLIGHT SHALLOWS]";
    ctx.fillStyle = "#78e6ff";
    if (this.depth > ZONE_TWILIGHT_MAX) { zone = "[MIDNIGHT ABYSS]"; ctx.fillStyle = "#ff5a5a"; }
    else if (this.depth > ZONE_SUNLIGHT_MAX) { zone = "[TWILIGHT TRENCH]"; ctx.fillStyle = "#b4a0ff"; }
    ctx.fillText(zone, CANVAS_WIDTH / 2, 46);

    // Score & Combo
    ctx.textAlign = "right";
    ctx.font = "bold 18px 'Share Tech Mono', monospace";
    ctx.fillStyle = "#ffd700";
    ctx.fillText(`SCORE: ${this.score.toString().padStart(5, '0')}`, CANVAS_WIDTH - 20, 26);
    ctx.font = "14px 'Share Tech Mono', monospace";
    ctx.fillStyle = "#8c96a5";
    ctx.fillText(`HI-SCORE: ${this.highScore.toString().padStart(5, '0')}`, CANVAS_WIDTH - 20, 48);

    if (this.combo > 1) {
      ctx.fillStyle = "#ffe63c";
      ctx.fillText(`COMBO: x${this.combo}!`, CANVAS_WIDTH - 20, 72);
      ctx.fillStyle = "#141923";
      ctx.fillRect(CANVAS_WIDTH - 120, 80, 100, 6);
      ctx.fillStyle = "#ffe63c";
      ctx.fillRect(CANVAS_WIDTH - 120, 80, 100 * (this.comboTimer / COMBO_TIMEOUT), 6);
    }

    // Bottom Abilities Bar
    ctx.textAlign = "left";
    ctx.font = "14px 'Share Tech Mono', monospace";
    const sonarReady = this.player.sonarTimer >= SONAR_COOLDOWN;
    ctx.fillStyle = sonarReady ? "#50e6ff" : "#728ca6";
    ctx.fillText(sonarReady ? "SPACE: SONAR [READY]" : `SPACE: SONAR [${Math.round((this.player.sonarTimer / SONAR_COOLDOWN) * 100)}%]`, 20, CANVAS_HEIGHT - 16);

    ctx.fillStyle = this.player.hasShield ? "#64f0ff" : "#5a6978";
    ctx.fillText(this.player.hasShield ? "SHIELD: ACTIVE [PROTECTED]" : "SHIELD: OFFLINE", 230, CANVAS_HEIGHT - 16);

    ctx.fillStyle = this.player.isBoosting ? "#ffe63c" : "#728ca6";
    ctx.fillText("SHIFT: BOOST", 480, CANVAS_HEIGHT - 16);

    ctx.textAlign = "right";
    ctx.fillStyle = "#728ca6";
    ctx.fillText("P: PAUSE | M: MUTE", CANVAS_WIDTH - 20, CANVAS_HEIGHT - 16);
    ctx.restore();
  }

  drawStartScreen() {
    const ctx = this.ctx;
    ctx.save();
    ctx.fillStyle = "rgba(2, 10, 24, 0.85)";
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    ctx.textAlign = "center";
    ctx.fillStyle = "#50e6ff";
    ctx.font = "bold 44px 'Trebuchet MS', sans-serif";
    ctx.fillText("ABYSSAL EXPEDITION", CANVAS_WIDTH / 2, 75);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 20px 'Trebuchet MS', sans-serif";
    ctx.fillText("2D DEEP SEA SUBMARINE SIMULATION", CANVAS_WIDTH / 2, 115);

    // Specification Card
    ctx.fillStyle = "rgba(10, 25, 45, 0.9)";
    ctx.strokeStyle = "#2878b4";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(CANVAS_WIDTH / 2 - 380, 145, 760, 310, 10);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#ffd700";
    ctx.font = "bold 18px 'Trebuchet MS', sans-serif";
    ctx.fillText("★ INDIVIDUAL LAB CUSTOMIZATION SPECIFICATION ★", CANVAS_WIDTH / 2, 175);

    const details = [
      ["Visual Theme:", "Ocean Depths / Abyssal Trench with dynamic depth zones & sun caustics"],
      ["Player Vessel:", "Deep Sea Research Submersible with animated propeller & headlight beam"],
      ["Collectibles:", "Luminescent Pearls (+100 pts) & Golden Clams (+350 pts & Oxygen restore)"],
      ["Hazards:", "Naval Depth Charges (drifting sea mines) & High-Speed Torpedoes"],
      ["Special Power-up:", "Oxygen Bubble Shield (absorbs 1 impact) & Sonar Radar Ping (SPACE)"],
      ["Physics Rule:", "Realistic water buoyancy lift & hydrodynamic drag deceleration"],
      ["Difficulty Rule:", "Increasing water depth scales torpedo speed, hazard frequency & light fade"],
    ];

    let y = 205;
    ctx.font = "14px 'Share Tech Mono', monospace";
    for (let [lbl, val] of details) {
      ctx.textAlign = "right";
      ctx.fillStyle = "#50e6ff";
      ctx.fillText(lbl, CANVAS_WIDTH / 2 - 130, y);
      ctx.textAlign = "left";
      ctx.fillStyle = "#ffffff";
      ctx.fillText(val, CANVAS_WIDTH / 2 - 110, y);
      y += 24;
    }

    ctx.textAlign = "center";
    ctx.fillStyle = "#ffe63c";
    ctx.font = "bold 15px 'Share Tech Mono', monospace";
    ctx.fillText("CONTROLS: WASD / Arrows: Steer | SPACE: Sonar Ping | SHIFT: Boost | P: Pause | R: Restart", CANVAS_WIDTH / 2, y + 14);

    ctx.font = "bold 22px 'Trebuchet MS', sans-serif";
    ctx.fillStyle = Math.floor(performance.now() * 0.003) % 2 === 0 ? "#ffd700" : "#ffffff";
    ctx.fillText("▶  PRESS SPACE OR CLICK TO DIVE  ◀", CANVAS_WIDTH / 2, 510);

    ctx.font = "14px 'Share Tech Mono', monospace";
    ctx.fillStyle = "#8c96a5";
    ctx.fillText(`CURRENT ALL-TIME RECORD: ${this.highScore.toString().padStart(5, '0')} PTS`, CANVAS_WIDTH / 2, 555);
    ctx.restore();
  }

  drawPauseScreen() {
    const ctx = this.ctx;
    ctx.save();
    ctx.fillStyle = "rgba(2, 8, 18, 0.75)";
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    ctx.textAlign = "center";
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 40px 'Trebuchet MS', sans-serif";
    ctx.fillText("EXPEDITION PAUSED", CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 - 30);

    ctx.fillStyle = "#50e6ff";
    ctx.font = "20px 'Trebuchet MS', sans-serif";
    ctx.fillText("Press P or ESC to Resume Navigation", CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 20);

    ctx.fillStyle = "#8c96a5";
    ctx.font = "14px 'Share Tech Mono', monospace";
    ctx.fillText("Press R to Restart Expedition", CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 55);
    ctx.restore();
  }

  drawGameOverScreen() {
    const ctx = this.ctx;
    ctx.save();
    ctx.fillStyle = "rgba(4, 8, 20, 0.9)";
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    ctx.textAlign = "center";
    ctx.fillStyle = "#ff3c3c";
    ctx.font = "bold 44px 'Trebuchet MS', sans-serif";
    ctx.fillText("MISSION TERMINATED", CANVAS_WIDTH / 2, 75);

    ctx.fillStyle = "#ff8c8c";
    ctx.font = "bold 16px 'Trebuchet MS', sans-serif";
    const cause = this.gameOverReason === "hull"
      ? "CAUSE: CATASTROPHIC HULL BREACH (PRESSURE IMPLOSION)"
      : "CAUSE: LIFE SUPPORT DEPLETION (OXYGEN STARVATION)";
    ctx.fillText(cause, CANVAS_WIDTH / 2, 115);

    // Telemetry Card
    ctx.fillStyle = "rgba(12, 22, 38, 0.9)";
    ctx.strokeStyle = "#325a8c";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(CANVAS_WIDTH / 2 - 280, 145, 560, 260, 10);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#50e6ff";
    ctx.font = "bold 18px 'Trebuchet MS', sans-serif";
    ctx.fillText("MISSION TELEMETRY LOG", CANVAS_WIDTH / 2, 175);

    const stats = [
      ["Final Score:", `${this.score.toString().padStart(5, '0')} PTS`],
      ["Maximum Depth Reached:", `${Math.round(this.depth)} meters`],
      ["Luminescent Pearls Harvested:", `${this.pearlsCollected}`],
      ["Golden Clams Discovered:", `${this.clamsCollected}`],
      ["Highest Combo Streak:", `x${this.maxComboStreak}`],
      ["All-Time High Score:", `${this.highScore.toString().padStart(5, '0')} PTS`],
    ];

    let y = 210;
    ctx.font = "15px 'Share Tech Mono', monospace";
    for (let [lbl, val] of stats) {
      ctx.textAlign = "left";
      ctx.fillStyle = "#ffffff";
      ctx.fillText(lbl, CANVAS_WIDTH / 2 - 240, y);
      ctx.textAlign = "right";
      ctx.fillStyle = "#ffd700";
      ctx.fillText(val, CANVAS_WIDTH / 2 + 240, y);
      y += 26;
    }

    ctx.textAlign = "center";
    ctx.font = "bold 22px 'Trebuchet MS', sans-serif";
    ctx.fillStyle = Math.floor(performance.now() * 0.003) % 2 === 0 ? "#ffd700" : "#ffffff";
    ctx.fillText("PRESS R OR CLICK TO DIVE AGAIN", CANVAS_WIDTH / 2, 480);

    ctx.font = "14px 'Share Tech Mono', monospace";
    ctx.fillStyle = "#728ca6";
    ctx.fillText("Multimedia Systems Lab Test 2 - 2D Arcade Game", CANVAS_WIDTH / 2, 540);
    ctx.restore();
  }

  loop(currentTime) {
    const dt = Math.min(0.05, (currentTime - this.lastTime) / 1000);
    this.lastTime = currentTime;

    this.update(dt);
    this.draw();

    requestAnimationFrame(this.loop);
  }
}

// Start game when page loads
window.addEventListener("DOMContentLoaded", () => {
  new Game();
});
