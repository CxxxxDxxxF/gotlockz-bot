import { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, PermissionFlagsBits } from 'discord.js';
import { logger } from '../utils/logger.js';

export const data = new SlashCommandBuilder()
  .setName('reactionrole')
  .setDescription('Create a reaction role message')
  .addStringOption(option =>
    option.setName('title')
      .setDescription('Title of the reaction role message')
      .setRequired(true))
  .addStringOption(option =>
    option.setName('description')
      .setDescription('Description of the roles')
      .setRequired(true))
  .addRoleOption(option =>
    option.setName('role1')
      .setDescription('First role to assign')
      .setRequired(true))
  .addStringOption(option =>
    option.setName('label1')
      .setDescription('Label for first role button')
      .setRequired(true))
  .addRoleOption(option =>
    option.setName('role2')
      .setDescription('Second role to assign')
      .setRequired(false))
  .addStringOption(option =>
    option.setName('label2')
      .setDescription('Label for second role button')
      .setRequired(false))
  .addRoleOption(option =>
    option.setName('role3')
      .setDescription('Third role to assign')
      .setRequired(false))
  .addStringOption(option =>
    option.setName('label3')
      .setDescription('Label for third role button')
      .setRequired(false))
  .setDefaultMemberPermissions(PermissionFlagsBits.ManageRoles);

export async function execute(interaction) {
  try {
    await interaction.deferReply({ ephemeral: true });

    const title = interaction.options.getString('title');
    const description = interaction.options.getString('description');
    const role1 = interaction.options.getRole('role1');
    const label1 = interaction.options.getString('label1');
    const role2 = interaction.options.getRole('role2');
    const label2 = interaction.options.getString('label2');
    const role3 = interaction.options.getRole('role3');
    const label3 = interaction.options.getString('label3');

    // Check permissions
    if (!interaction.member.permissions.has(PermissionFlagsBits.ManageRoles)) {
      await interaction.editReply({
        content: '❌ You need Manage Roles permission to create reaction roles.',
        ephemeral: true
      });
      return;
    }

    // Create embed
    const embed = new EmbedBuilder()
      .setColor(0x0099ff)
      .setTitle(title)
      .setDescription(description)
      .addFields(
        { name: '📋 Available Roles', value: 'Click the buttons below to get your roles!' }
      )
      .setTimestamp()
      .setFooter({ text: 'GotLockz Bot - Role Management' });

    // Create buttons
    const buttons = [];
    
    // First role (required)
    buttons.push(
      new ButtonBuilder()
        .setCustomId(`role_${role1.id}`)
        .setLabel(label1)
        .setStyle(ButtonStyle.Primary)
    );

    // Second role (optional)
    if (role2 && label2) {
      buttons.push(
        new ButtonBuilder()
          .setCustomId(`role_${role2.id}`)
          .setLabel(label2)
          .setStyle(ButtonStyle.Secondary)
      );
    }

    // Third role (optional)
    if (role3 && label3) {
      buttons.push(
        new ButtonBuilder()
          .setCustomId(`role_${role3.id}`)
          .setLabel(label3)
          .setStyle(ButtonStyle.Success)
      );
    }

    const actionRow = new ActionRowBuilder().addComponents(buttons);

    // Send message
    const message = await interaction.channel.send({
      embeds: [embed],
      components: [actionRow]
    });

    logger.info('Reaction role message created', {
      messageId: message.id,
      channelId: interaction.channel.id,
      roles: [role1.id, role2?.id, role3?.id].filter(Boolean),
      createdBy: interaction.user.id
    });

    await interaction.editReply({
      content: '✅ Reaction role message created successfully!',
      ephemeral: true
    });

  } catch (error) {
    logger.error('Reaction role command failed:', error);
    await interaction.editReply({
      content: '❌ An error occurred while creating the reaction role message.',
      ephemeral: true
    });
  }
} 