'use strict';

const pipeCount = 30;
const pipePropCount = 8;
const pipePropsLength = pipeCount * pipePropCount;
const turnCount = 8;
const turnAmount = (360 / turnCount) * TO_RAD;
const turnChanceRange = 58;
const baseSpeed = 0.5;
const rangeSpeed = 1;
const baseTTL = 100;
const rangeTTL = 300;
const baseWidth = 2;
const rangeWidth = 4;
const baseHue = 32;
const rangeHue = 10;

let container;
let canvas;
let ctx;
let center;
let tick;
let pipeProps;

function setup() {
  createCanvas();
  resize();
  initPipes();
  draw();
}

function initPipes() {
  pipeProps = new Float32Array(pipePropsLength);
  for (let i = 0; i < pipePropsLength; i += pipePropCount) {
    initPipe(i);
  }
}

function initPipe(i) {
  const x = rand(canvas.a.width);
  const y = center[1];
  const direction = (round(rand(1)) ? HALF_PI : TAU - HALF_PI);
  const speed = baseSpeed + rand(rangeSpeed);
  const life = 0;
  const ttl = baseTTL + rand(rangeTTL);
  const width = baseWidth + rand(rangeWidth);
  const hue = baseHue + rand(rangeHue);

  pipeProps.set([x, y, direction, speed, life, ttl, width, hue], i);
}

function updatePipes() {
  tick++;
  for (let i = 0; i < pipePropsLength; i += pipePropCount) {
    updatePipe(i);
  }
}

function updatePipe(i) {
  let x = pipeProps[i];
  let y = pipeProps[i + 1];
  let direction = pipeProps[i + 2];
  const speed = pipeProps[i + 3];
  let life = pipeProps[i + 4];
  const ttl = pipeProps[i + 5];
  const width = pipeProps[i + 6];
  const hue = pipeProps[i + 7];

  drawPipe(x, y, life, ttl, width, hue);

  life++;
  x += cos(direction) * speed;
  y += sin(direction) * speed;
  const turnChance = !(tick % round(rand(turnChanceRange))) && (!(round(x) % 6) || !(round(y) % 6));
  const turnBias = round(rand(1)) ? -1 : 1;
  direction += turnChance ? turnAmount * turnBias : 0;

  pipeProps[i] = x;
  pipeProps[i + 1] = y;
  pipeProps[i + 2] = direction;
  pipeProps[i + 4] = life;

  checkBounds(x, y);
  if (life > ttl) initPipe(i);
}

function drawPipe(x, y, life, ttl, width, hue) {
  ctx.a.save();
  ctx.a.strokeStyle = `hsla(${hue}, 100%, 85%, ${fadeInOut(life, ttl) * 0.2})`;
  ctx.a.beginPath();
  ctx.a.arc(x, y, width, 0, TAU);
  ctx.a.stroke();
  ctx.a.closePath();
  ctx.a.restore();
}

function checkBounds(x, y) {
  if (x > canvas.a.width) x = 0;
  if (x < 0) x = canvas.a.width;
  if (y > canvas.a.height) y = 0;
  if (y < 0) y = canvas.a.height;
}

function createCanvas() {
  container = document.querySelector('.content--canvas');
  canvas = {
    a: document.createElement('canvas'),
    b: document.createElement('canvas')
  };
  canvas.b.style = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
  `;
  container.appendChild(canvas.b);
  ctx = {
    a: canvas.a.getContext('2d'),
    b: canvas.b.getContext('2d')
  };
  center = [];
  tick = 0;
}

function resize() {
  const { innerWidth, innerHeight } = window;

  canvas.a.width = innerWidth;
  canvas.a.height = innerHeight;
  canvas.b.width = innerWidth;
  canvas.b.height = innerHeight;

  center[0] = 0.5 * canvas.a.width;
  center[1] = 0.5 * canvas.a.height;
}

function render() {
  // Fade old trails (semi-transparent background fill)
  ctx.b.save();
  ctx.b.fillStyle = 'hsla(36, 100%, 5%, 0.07)';
  ctx.b.fillRect(0, 0, canvas.b.width, canvas.b.height);
  ctx.b.restore();

  // Add blur
  ctx.b.save();
  ctx.b.filter = 'blur(6px)';
  ctx.b.drawImage(canvas.a, 0, 0);
  ctx.b.restore();

  // Add sharp trails
  ctx.b.save();
  ctx.b.drawImage(canvas.a, 0, 0);
  ctx.b.restore();
}

function draw() {
  updatePipes();
  render();
  window.requestAnimationFrame(draw);
}

window.addEventListener('load', setup);
window.addEventListener('resize', resize);
