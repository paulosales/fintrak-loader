import fs from 'fs';
import mysql from 'mysql2/promise';
import csv from 'csv-parser';
import dotenv from 'dotenv';
import crypto from 'crypto';
import createDebug from 'debug';

dotenv.config();

createDebug.enable(process.env.DEBUG || 'app:*');

const debug = createDebug('app:import');
const error = createDebug('app:error');

const BATCH_SIZE = 100;

const TYPE_MAP = {
  PURCHASE: 1,
  PAYMENT: 2,
  REFUND: 3,
  INTEREST: 4
};

function parseDate(date, time) {
  const [month, day, year] = date.split('/');
  return new Date(`${year}-${month}-${day} ${time}`);
}

function generateFingerprint(datetime, amount, description) {
  const raw = `${datetime}|${amount}|${description}`;
  return crypto.createHash('md5').update(raw).digest('hex');
}

const fileName = process.argv[2];

if (!fileName) {
  error('Usage: node script.js <csv-file>');
  process.exit(1);
}

if (!fs.existsSync(fileName)) {
  error(`File not found: ${fileName}`);
  process.exit(1);
}

(async () => {
  const connection = await mysql.createConnection({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  });

  const rows = [];

  fs.createReadStream(fileName)
    .pipe(csv())
    .on('data', (row) => {
      const datetime = parseDate(row.Date, row.Time)
        .toISOString()
        .slice(0, 19)
        .replace('T', ' ');

      const amount = parseFloat(row.Amount);
      const description = row.Description;

      const fingerprint = generateFingerprint(datetime, amount, description);

      rows.push([
        1,
        TYPE_MAP[row.Type] || 1,
        datetime,
        amount,
        description,
        null,
        fingerprint
      ]);
    })
    .on('end', async () => {
      for (let i = 0; i < rows.length; i += BATCH_SIZE) {
        const batch = rows.slice(i, i + BATCH_SIZE);

        await connection.query(
          `INSERT IGNORE INTO transactions 
          (account_id, transaction_type_id, datetime, amount, description, note, fingerprint)
          VALUES ?`,
          [batch]
        );

        debug(`Processed batch ${i / BATCH_SIZE + 1}`);
      }

      await connection.end();
      debug('Done!');
    })
    .on('error', (err) => {
      error('Stream error:', err);
    });
})();