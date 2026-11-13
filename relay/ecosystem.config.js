// PM2 config for the Fontes relay. Start: pm2 start ecosystem.config.js
// Only this app is defined here, so pm2 start/reload of this file touches nothing else.
module.exports = {
  apps: [{
    name: "fontes-relay",
    script: "relay.py",
    interpreter: "python3",
    cwd: __dirname,
    env: {
      RELAY_HOST: "127.0.0.1",   // nginx in front; never exposed directly
      RELAY_PORT: "4020",        // check it is free first: ss -ltnp | grep 4020
      RELAY_DB: __dirname + "/data/relay.sqlite3",
    },
    max_memory_restart: "100M",
    restart_delay: 5000,
  }],
};
