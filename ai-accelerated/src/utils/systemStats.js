import os from 'os';

export async function getSystemStats () {
  const uptime = process.uptime();
  const memoryUsage = process.memoryUsage();
  const cpuUsage = os.loadavg();

  // Format uptime
  const hours = Math.floor(uptime / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);
  const seconds = Math.floor(uptime % 60);
  const uptimeFormatted = `${hours}h ${minutes}m ${seconds}s`;

  // Format memory usage
  const memoryMB = Math.round(memoryUsage.heapUsed / 1024 / 1024);
  const memoryTotalMB = Math.round(memoryUsage.heapTotal / 1024 / 1024);
  const memoryFormatted = `${memoryMB}MB / ${memoryTotalMB}MB`;

  // Format CPU usage
  const cpuFormatted = `${(cpuUsage[0] * 100).toFixed(1)}%`;

  // Get command count (placeholder)
  const commandsFormatted = '2 commands loaded';

  // Get server count
  const serversFormatted = `${global.client?.guilds?.cache?.size || 0} servers`;

  return {
    uptime: uptimeFormatted,
    memory: memoryFormatted,
    cpu: cpuFormatted,
    commands: commandsFormatted,
    servers: serversFormatted
  };
}
