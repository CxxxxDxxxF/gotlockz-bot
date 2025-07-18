import { Events } from 'discord.js';
import { logger } from '../utils/logger.js';

export function setupInteractionHandler(client) {
  client.on(Events.InteractionCreate, async (interaction) => {
    try {
      // Handle slash commands
      if (interaction.isChatInputCommand()) {
        const command = client.commands.get(interaction.commandName);
        if (!command) {
          logger.error(`Command not found: ${interaction.commandName}`);
          return;
        }

        await command.execute(interaction);
        return;
      }

      // Handle button interactions
      if (interaction.isButton()) {
        await handleButtonInteraction(interaction);
        return;
      }

      // Handle modal submissions
      if (interaction.isModalSubmit()) {
        await handleModalSubmission(interaction);
        return;
      }

    } catch (error) {
      logger.error('Interaction handler error:', error);
      
      const errorMessage = '❌ An error occurred while processing this interaction.';
      
      if (interaction.replied || interaction.deferred) {
        await interaction.followUp({ content: errorMessage, ephemeral: true });
      } else {
        await interaction.reply({ content: errorMessage, ephemeral: true });
      }
    }
  });
}

async function handleButtonInteraction(interaction) {
  const { customId } = interaction;

  try {
    // Handle suggestion buttons
    if (customId.startsWith('suggest_')) {
      await handleSuggestionButton(interaction);
      return;
    }

    // Handle giveaway buttons
    if (customId.startsWith('giveaway_')) {
      await handleGiveawayButton(interaction);
      return;
    }

    // Handle role buttons
    if (customId.startsWith('role_')) {
      await handleRoleButton(interaction);
      return;
    }

    // Unknown button
    await interaction.reply({
      content: '❌ Unknown button interaction.',
      ephemeral: true
    });

  } catch (error) {
    logger.error('Button interaction error:', error);
    await interaction.reply({
      content: '❌ An error occurred while processing this button.',
      ephemeral: true
    });
  }
}

async function handleSuggestionButton(interaction) {
  const { customId } = interaction;
  const message = interaction.message;
  const embed = message.embeds[0];

  // Check if user has permission to manage suggestions
  if (!interaction.member.permissions.has('ManageGuild') && interaction.user.id !== process.env.OWNER_ID) {
    await interaction.reply({
      content: '❌ You need Manage Server permissions to manage suggestions.',
      ephemeral: true
    });
    return;
  }

  let newStatus, newColor, actionText;

  switch (customId) {
    case 'suggest_approve':
      newStatus = '🟢 Approved';
      newColor = 0x51cf66;
      actionText = 'approved';
      break;
    case 'suggest_deny':
      newStatus = '🔴 Denied';
      newColor = 0xff6b6b;
      actionText = 'denied';
      break;
    case 'suggest_implement':
      newStatus = '🚀 Implemented';
      newColor = 0x339af0;
      actionText = 'marked as implemented';
      break;
    default:
      return;
  }

  // Update embed
  embed.setColor(newColor);
  embed.spliceFields(2, 1, { name: '📊 Status', value: newStatus, inline: true });

  // Disable all buttons
  const actionRow = interaction.message.components[0];
  actionRow.components.forEach(button => {
    button.setDisabled(true);
  });

  await message.edit({
    embeds: [embed],
    components: [actionRow]
  });

  await interaction.reply({
    content: `✅ Suggestion ${actionText} successfully!`,
    ephemeral: true
  });

  logger.info('Suggestion action taken', {
    messageId: message.id,
    action: customId,
    moderator: interaction.user.id
  });
}

async function handleGiveawayButton(interaction) {
  const { customId } = interaction;

  if (customId === 'giveaway_enter') {
    // Handle giveaway entry
    const message = interaction.message;
    const embed = message.embeds[0];
    
    // This would typically check against a database
    // For now, we'll just acknowledge the entry
    await interaction.reply({
      content: '🎉 You have entered the giveaway! Good luck!',
      ephemeral: true
    });

    logger.info('User entered giveaway', {
      messageId: message.id,
      userId: interaction.user.id
    });
  }
}

async function handleRoleButton(interaction) {
  const { customId } = interaction;
  const roleId = customId.replace('role_', '');
  const role = interaction.guild.roles.cache.get(roleId);

  if (!role) {
    await interaction.reply({
      content: '❌ Role not found.',
      ephemeral: true
    });
    return;
  }

  const member = interaction.member;
  const hasRole = member.roles.cache.has(roleId);

  try {
    if (hasRole) {
      await member.roles.remove(role);
      await interaction.reply({
        content: `❌ Removed role **${role.name}** from you.`,
        ephemeral: true
      });
    } else {
      await member.roles.add(role);
      await interaction.reply({
        content: `✅ Added role **${role.name}** to you.`,
        ephemeral: true
      });
    }

    logger.info('Role assignment', {
      userId: interaction.user.id,
      roleId,
      action: hasRole ? 'removed' : 'added',
      guildId: interaction.guild.id
    });

  } catch (error) {
    logger.error('Role assignment error:', error);
    await interaction.reply({
      content: '❌ Failed to manage role. Please contact an administrator.',
      ephemeral: true
    });
  }
}

async function handleModalSubmission(interaction) {
  const { customId } = interaction;

  try {
    // Handle different modal submissions
    switch (customId) {
      case 'suggestion_modal':
        await handleSuggestionModal(interaction);
        break;
      default:
        await interaction.reply({
          content: '❌ Unknown modal submission.',
          ephemeral: true
        });
    }
  } catch (error) {
    logger.error('Modal submission error:', error);
    await interaction.reply({
      content: '❌ An error occurred while processing your submission.',
      ephemeral: true
    });
  }
}

async function handleSuggestionModal(interaction) {
  const suggestion = interaction.fields.getTextInputValue('suggestion_input');
  
  // This would typically save to a database
  logger.info('Suggestion submitted via modal', {
    userId: interaction.user.id,
    suggestion
  });

  await interaction.reply({
    content: '✅ Your suggestion has been submitted successfully!',
    ephemeral: true
  });
} 