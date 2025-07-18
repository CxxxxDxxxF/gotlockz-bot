export function getSystemStats () {
  const stats = {
    uptime: `${Math.floor(process.uptime() / 3600)}h ${Math.floor((process.uptime() % 3600) / 60)}m`,
    memory: `${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`,
    cpu: `${Math.round(process.cpuUsage().user / 1000)}ms`,
    commands: '2', // admin, pick
    servers: '1' // Current guild
  };

  return stats;
}
