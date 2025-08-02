# Pick Command Update - Units Option

## Overview

The `/pick` command has been updated to replace the "notes" option with a "units" option that is specifically designed for VIP plays.

## Changes Made

### 1. Command Structure Update
- **Removed**: `notes` option (was optional for all play types)
- **Added**: `units` option (required for VIP plays only)

### 2. Validation Logic
- **VIP Plays**: Units are **required** - users must specify units (e.g., "2u", "1.5u")
- **Free Plays**: Units are **not allowed** - option will be ignored with a warning
- **Lotto Tickets**: Units are **not allowed** - option will be ignored with a warning

### 3. User Experience
- Clear error messages guide users on proper usage
- Units format accepts both "2u" and "2 units" formats
- Validation happens before processing to save time

## Usage Examples

### ✅ Correct Usage

**VIP Play with Units:**
```
/pick channel_type:VIP Play image:[bet slip] units:2u
/pick channel_type:VIP Play image:[bet slip] units:1.5u
```

**Free Play (no units):**
```
/pick channel_type:Free Play image:[bet slip]
```

**Lotto Ticket (no units):**
```
/pick channel_type:Lotto Ticket image:[bet slip]
```

### ❌ Incorrect Usage

**VIP Play without Units:**
```
/pick channel_type:VIP Play image:[bet slip]
```
*Error: "Units are required for VIP plays. Please specify units (e.g., 2u, 1.5u)."*

**Free Play with Units:**
```
/pick channel_type:Free Play image:[bet slip] units:2u
```
*Warning: "Units option is only available for VIP plays. Please remove the units option or select VIP Play."*

## Technical Implementation

### Files Modified
1. `src/commands/pick.js` - Main command logic
2. `src/config/commands.json` - Command configuration
3. Updated validation and error handling

### Validation Logic
```javascript
// VIP plays require units
if (channelType === 'vip_plays' && !units) {
  return '❌ Units are required for VIP plays. Please specify units (e.g., 2u, 1.5u).';
}

// Non-VIP plays should not have units
if (channelType !== 'vip_plays' && units) {
  return '⚠️ Units option is only available for VIP plays. Please remove the units option or select VIP Play.';
}
```

## Benefits

1. **Clearer Intent**: VIP plays now explicitly require units specification
2. **Better UX**: Users get immediate feedback on proper usage
3. **Consistency**: Aligns with betting community standards
4. **Validation**: Prevents processing errors by catching issues early

## Testing

The update has been tested with:
- ✅ Command loading and structure validation
- ✅ Units parsing from various formats
- ✅ Validation logic for all channel types
- ✅ Error message accuracy

## Next Steps

1. Deploy the updated command to Discord
2. Test with real users in Discord environment
3. Monitor for any edge cases or user feedback
4. Consider adding units format validation (e.g., decimal limits) 