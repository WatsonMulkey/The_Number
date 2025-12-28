// Simple icon generator for PWA
// Creates placeholder icons with The Number branding

import { createCanvas } from 'canvas';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function generateIcon(size) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');

  // Background - Soft Cream (#E9F5DB)
  ctx.fillStyle = '#E9F5DB';
  ctx.fillRect(0, 0, size, size);

  // Circle background - Sage Green (#87986A)
  ctx.fillStyle = '#87986A';
  ctx.beginPath();
  ctx.arc(size / 2, size / 2, size * 0.4, 0, Math.PI * 2);
  ctx.fill();

  // Text - "The Number"
  ctx.fillStyle = '#2D5016'; // Forest Green for contrast
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.font = `bold ${size * 0.15}px Arial`;
  ctx.fillText('THE', size / 2, size / 2 - size * 0.08);
  ctx.font = `bold ${size * 0.12}px Arial`;
  ctx.fillText('NUMBER', size / 2, size / 2 + size * 0.08);

  // Save PNG
  const buffer = canvas.toBuffer('image/png');
  const filename = path.join(__dirname, 'public', `icon-${size}.png`);
  fs.writeFileSync(filename, buffer);
  console.log(`✓ Created ${filename}`);
}

// Create public directory if it doesn't exist
const publicDir = path.join(__dirname, 'public');
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir);
}

// Generate both required sizes
generateIcon(192);
generateIcon(512);

console.log('✅ PWA icons generated successfully!');
