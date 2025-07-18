import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { logger } from '../utils/logger.js';

export const data = new SlashCommandBuilder()
  .setName('help')
  .setDescription('Shows available commands and their usage')
  .addStringOption(option =>
    option.setName('command')
      .setDescription('Get help for a specific command')
      .setRequired(false));

export async function execute(interaction) {
  try {
    const commandName = interaction.options.getString('command');
    
    if (commandName) {
      await showCommandHelp(interaction, commandName);
    } else {
      await showGeneralHelp(interaction);
    }
    
    logger.command('help', interaction.user.id, { commandName });
    
  } catch (error) {
    logger.error('Help command failed:', error);
    await interaction.reply({ 
      content: 'Sorry, there was an error showing the help information.', 
      ephemeral: true 
    });
  }
}

async function showGeneralHelp(interaction) {
  const embed = new EmbedBuilder()
    .setColor(0x0099FF)
    .setTitle('🎯 GotLockz Family - Command Center')
    .setDescription('Here are all the available commands for your MLB betting analysis!')
    .addFields(
      {
        name: '📊 **Betting Commands**',
        value: [
          '`/pick` - Get today\'s betting pick',
          '`/stats` - View team statistics',
          '`/odds` - Check current odds',
          '`/weather` - Get weather impact analysis'
        ].join('\n'),
        inline: false
      },
      {
        name: '🔧 **Utility Commands**',
        value: [
          '`/help` - Show this help message',
          '`/status` - Check bot status',
          '`/ping` - Test bot response time'
        ].join('\n'),
        inline: false
      },
      {
        name: '💰 **Remember**',
        value: '21+ only • Please bet responsibly • GotLockz Family',
        inline: false
      }
    )
    .setFooter({ 
      text: 'GotLockz Family | Use /help <command> for detailed info' 
    })
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
}

async function showCommandHelp(interaction, commandName) {
  const commandHelp = {
    pick: {
      title: '🎯 /pick Command',
      description: 'Get today\'s betting pick with detailed analysis',
      usage: '/pick [team]',
      examples: [
        '/pick - Get today\'s main pick',
        '/pick Yankees - Get pick for Yankees game'
      ],
      fields: [
        {
          name: 'What you get:',
          value: '• Betting recommendation\n• Odds and confidence level\n• Detailed analysis\n• Weather impact\n• Team statistics'
        }
      ]
    },
    stats: {
      title: '📊 /stats Command',
      description: 'View comprehensive team and player statistics',
      usage: '/stats <team> [player]',
      examples: [
        '/stats Yankees - Team stats',
        '/stats Yankees Judge - Player stats'
      ],
      fields: [
        {
          name: 'Available stats:',
          value: '• Team batting/pitching\n• Player performance\n• Head-to-head records\n• Recent form'
        }
      ]
    },
    odds: {
      title: '💰 /odds Command',
      description: 'Check current betting odds for games',
      usage: '/odds [team]',
      examples: [
        '/odds - All today\'s odds',
        '/odds Dodgers - Dodgers odds'
      ],
      fields: [
        {
          name: 'Odds types:',
          value: '• Moneyline\n• Run line\n• Over/Under\n• Player props'
        }
      ]
    },
    weather: {
      title: '🌤️ /weather Command',
      description: 'Get weather impact analysis for games',
      usage: '/weather [team]',
      examples: [
        '/weather - Today\'s weather impacts',
        '/weather Red Sox - Red Sox game weather'
      ],
      fields: [
        {
          name: 'Weather factors:',
          value: '• Temperature\n• Wind direction/speed\n• Humidity\n• Precipitation chance'
        }
      ]
    }
  };

  const help = commandHelp[commandName.toLowerCase()];
  
  if (!help) {
    await interaction.reply({ 
      content: `❌ Command \`${commandName}\` not found. Use \`/help\` to see all available commands.`, 
      ephemeral: true 
    });
    return;
  }

  const embed = new EmbedBuilder()
    .setColor(0x0099FF)
    .setTitle(help.title)
    .setDescription(help.description)
    .addFields(
      {
        name: '📝 Usage',
        value: `\`${help.usage}\``,
        inline: false
      },
      {
        name: '💡 Examples',
        value: help.examples.map(ex => `\`${ex}\``).join('\n'),
        inline: false
      },
      ...help.fields
    )
    .setFooter({ 
      text: 'GotLockz Family | 21+ Only | Please bet responsibly' 
    })
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
} 