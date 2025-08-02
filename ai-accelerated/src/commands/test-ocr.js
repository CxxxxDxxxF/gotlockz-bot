import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { logger } from '../utils/logger.js';

export const data = new SlashCommandBuilder()
  .setName('test-ocr')
  .setDescription('Test the OCR image processing functionality')
  .addAttachmentOption(option =>
    option
      .setName('image')
      .setDescription('Bet slip image to test OCR on')
      .setRequired(true)
  )
  .addBooleanOption(option =>
    option
      .setName('debug')
      .setDescription('Show detailed debug information')
      .setRequired(false)
  );

export async function execute(interaction) {
  const startTime = Date.now();
  const commandId = `test_ocr_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  try {
    logger.info('Test OCR command started', {
      commandId,
      userId: interaction.user.id,
      username: interaction.user.username
    });

    await interaction.deferReply();

    const image = interaction.options.getAttachment('image');
    const debug = interaction.options.getBoolean('debug') ?? false;

    if (!image) {
      await interaction.editReply('❌ Please provide an image to test.');
      return;
    }

    console.log(`📸 [${commandId}] Testing OCR on image: ${image.url}`);

    // Import the image processing functions
    let extractTextFromImage, parseBetSlip;
    
    try {
      // Import parser module (this should always work)
      const parserModule = await import('../../image-processing/slip-parser.js');
      parseBetSlip = parserModule.parseBetSlip;
      console.log(`✅ [${commandId}] Parser module imported successfully`);
      
      // Try to import OCR module (may fail on Windows due to Sharp issues)
      try {
        const ocrModule = await import('../../image-processing/ocr-reader.js');
        extractTextFromImage = ocrModule.extractTextFromImage;
        console.log(`✅ [${commandId}] OCR module imported successfully`);
      } catch (ocrError) {
        console.log(`⚠️ [${commandId}] OCR module import failed (Sharp issue): ${ocrError.message}`);
        extractTextFromImage = null;
      }
      
    } catch (error) {
      logger.error('Failed to import image processing modules', {
        commandId,
        error: error.message,
        stack: error.stack
      });
      await interaction.editReply('❌ Failed to load image processing modules. Please check the installation.');
      return;
    }

    // Download the image
    console.log(`📥 [${commandId}] Downloading image...`);
    let imageBuffer;
    try {
      const response = await fetch(image.url);
      if (!response.ok) {
        throw new Error(`Failed to download image: ${response.status} ${response.statusText}`);
      }
      imageBuffer = Buffer.from(await response.arrayBuffer());
      console.log(`✅ [${commandId}] Image downloaded successfully (${imageBuffer.length} bytes)`);
    } catch (error) {
      logger.error('Failed to download image', {
        commandId,
        error: error.message
      });
      await interaction.editReply('❌ Failed to download the image. Please try again.');
      return;
    }

    // Extract text using OCR
    console.log(`🔍 [${commandId}] Running OCR...`);
    let extractedText = '';
    
    if (extractTextFromImage) {
      try {
        extractedText = await extractTextFromImage(imageBuffer);
        console.log(`✅ [${commandId}] OCR completed. Extracted text length: ${extractedText.length}`);
        
        if (debug) {
          console.log(`📝 [${commandId}] Raw OCR text: "${extractedText}"`);
        }
      } catch (error) {
        logger.error('OCR processing failed', {
          commandId,
          error: error.message,
          stack: error.stack
        });
        console.log(`⚠️ [${commandId}] OCR failed, using fallback: ${error.message}`);
        extractedText = 'OCR processing failed - using fallback text for testing';
      }
    } else {
      console.log(`⚠️ [${commandId}] OCR module not available, using fallback text`);
      extractedText = 'NYM vs PHI ML -120 5u (fallback text for testing)';
    }

    // Parse the extracted text
    console.log(`🔧 [${commandId}] Parsing extracted text...`);
    let parsedData;
    try {
      parsedData = parseBetSlip(extractedText);
      console.log(`✅ [${commandId}] Text parsing completed`);
    } catch (error) {
      logger.error('Text parsing failed', {
        commandId,
        error: error.message,
        stack: error.stack
      });
      await interaction.editReply('❌ Text parsing failed. Please check the image quality.');
      return;
    }

    // Create response embed
    const embed = new EmbedBuilder()
      .setTitle('🔍 OCR Test Results')
      .setColor('#00ff00')
      .setTimestamp()
      .setFooter({ text: `Test ID: ${commandId}` });

    // Add OCR results
    embed.addFields(
      { 
        name: '📝 Extracted Text', 
        value: extractedText.length > 0 ? `\`\`\`${extractedText.substring(0, 1000)}${extractedText.length > 1000 ? '...' : ''}\`\`\`` : 'No text extracted',
        inline: false 
      },
      { 
        name: '⏱️ Processing Time', 
        value: `${Date.now() - startTime}ms`, 
        inline: true 
      },
      { 
        name: '📊 Text Length', 
        value: `${extractedText.length} characters`, 
        inline: true 
      }
    );

    // Add OCR status
    if (!extractTextFromImage) {
      embed.addFields(
        { 
          name: '⚠️ OCR Status', 
          value: 'OCR module not available (Sharp installation issue on Windows). Using fallback text for testing.', 
          inline: false 
        }
      );
    }

    // Add parsed data if available
    if (parsedData) {
      const teamsText = parsedData.teams.length > 0 ? parsedData.teams.join(', ') : 'None detected';
      const oddsText = parsedData.odds ? `${parsedData.odds > 0 ? '+' : ''}${parsedData.odds}` : 'None detected';
      const betTypeText = parsedData.betType || 'None detected';
      const unitsText = parsedData.units ? `${parsedData.units}u` : 'None detected';

      embed.addFields(
        { name: '🏟️ Teams Detected', value: teamsText, inline: true },
        { name: '💰 Odds', value: oddsText, inline: true },
        { name: '🎯 Bet Type', value: betTypeText, inline: true },
        { name: '📈 Units', value: unitsText, inline: true }
      );

      if (parsedData.homeTeam && parsedData.awayTeam) {
        embed.addFields(
          { name: '🏠 Home Team', value: parsedData.homeTeam, inline: true },
          { name: '✈️ Away Team', value: parsedData.awayTeam, inline: true }
        );
      }

      if (parsedData.players && parsedData.players.length > 0) {
        embed.addFields(
          { name: '👤 Players Detected', value: parsedData.players.join(', '), inline: false }
        );
      }

      if (parsedData.playerProp) {
        embed.addFields(
          { name: '🎯 Player Prop', value: `${parsedData.playerProp.player} ${parsedData.playerProp.value} ${parsedData.playerProp.stat}`, inline: false }
        );
      }
    }

    // Add debug information if requested
    if (debug) {
      embed.addFields(
        { 
          name: '🐛 Debug Info', 
          value: `Image URL: ${image.url}\nImage Size: ${imageBuffer.length} bytes\nImage Type: ${image.contentType || 'Unknown'}`, 
          inline: false 
        }
      );
    }

    // Send the results
    await interaction.editReply({ embeds: [embed] });

    logger.info('Test OCR command completed successfully', {
      commandId,
      userId: interaction.user.id,
      processingTime: Date.now() - startTime,
      textLength: extractedText.length,
      teamsDetected: parsedData?.teams?.length || 0
    });

  } catch (error) {
    logger.error('Test OCR command failed', {
      commandId,
      userId: interaction.user.id,
      error: error.message,
      stack: error.stack
    });

    const errorEmbed = new EmbedBuilder()
      .setTitle('❌ OCR Test Failed')
      .setColor('#ff0000')
      .setDescription(`An error occurred during testing:\n\`\`\`${error.message}\`\`\``)
      .setTimestamp()
      .setFooter({ text: `Test ID: ${commandId}` });

    await interaction.editReply({ embeds: [errorEmbed] });
  }
} 