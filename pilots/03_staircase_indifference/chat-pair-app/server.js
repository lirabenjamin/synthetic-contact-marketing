const express = require('express');
const http = require('http');
const path = require('path');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.use(express.static(path.join(__dirname, 'public')));

app.get('/healthz', (req, res) => {
  res.json({
    ok: true,
    waiting: { Democrat: waiting.Democrat.length, Republican: waiting.Republican.length },
    rooms: Object.keys(rooms).length,
  });
});

const CHAT_DURATION_MS = 3 * 60 * 1000;
const WAIT_TIMEOUT_MS  = 2 * 60 * 1000;

const waiting = { Democrat: [], Republican: [] };
const rooms = {};

function tryPair() {
  while (waiting.Democrat.length && waiting.Republican.length) {
    const a = waiting.Democrat.shift();
    const b = waiting.Republican.shift();
    clearTimeout(a.waitTimer);
    clearTimeout(b.waitTimer);

    const roomId = 'room_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
    a.socket.join(roomId);
    b.socket.join(roomId);
    a.socket.data.roomId = roomId;
    b.socket.data.roomId = roomId;

    const endsAt = Date.now() + CHAT_DURATION_MS;
    const timer = setTimeout(() => {
      io.to(roomId).emit('chatEnded', { reason: 'timeout' });
      delete rooms[roomId];
    }, CHAT_DURATION_MS);
    rooms[roomId] = { a, b, endsAt, timer };

    io.to(roomId).emit('matched', { roomId, endsAt });
    console.log(`[pair] ${a.qualtricsId} (Dem) <-> ${b.qualtricsId} (Rep) in ${roomId}`);
  }
}

io.on('connection', (socket) => {
  socket.on('join', ({ party, qualtricsId }) => {
    if (!['Democrat', 'Republican'].includes(party)) {
      socket.emit('joinError', 'invalid party');
      return;
    }
    socket.data.party = party;
    socket.data.qualtricsId = String(qualtricsId || 'anon').slice(0, 64);

    const entry = {
      socket,
      qualtricsId: socket.data.qualtricsId,
      joinedAt: Date.now(),
      waitTimer: setTimeout(() => {
        const idx = waiting[party].indexOf(entry);
        if (idx >= 0) waiting[party].splice(idx, 1);
        if (!socket.data.roomId) socket.emit('noMatch');
      }, WAIT_TIMEOUT_MS),
    };
    waiting[party].push(entry);
    socket.data.waitEntry = entry;
    socket.emit('waiting');
    console.log(`[join] ${socket.data.qualtricsId} as ${party} (queue: D=${waiting.Democrat.length} R=${waiting.Republican.length})`);
    tryPair();
  });

  socket.on('message', (text) => {
    const roomId = socket.data.roomId;
    if (!roomId || !rooms[roomId]) return;
    const msg = {
      from: socket.data.qualtricsId,
      text: String(text).slice(0, 1000),
      ts: Date.now(),
    };
    io.to(roomId).emit('message', msg);
  });

  socket.on('disconnect', () => {
    if (socket.data.party && socket.data.waitEntry) {
      const q = waiting[socket.data.party];
      const idx = q.indexOf(socket.data.waitEntry);
      if (idx >= 0) q.splice(idx, 1);
      clearTimeout(socket.data.waitEntry.waitTimer);
    }
    const roomId = socket.data.roomId;
    if (roomId && rooms[roomId]) {
      socket.to(roomId).emit('partnerLeft');
      clearTimeout(rooms[roomId].timer);
      delete rooms[roomId];
    }
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`staircase-chat-pair listening on ${PORT}`);
});
