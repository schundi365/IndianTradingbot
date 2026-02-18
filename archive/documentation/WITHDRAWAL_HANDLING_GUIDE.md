# Handling Withdrawals and Deposits

## The Problem

The bot tracks peak balance to calculate drawdown and protect your account. However, it cannot distinguish between:

- **Trading losses** (should trigger drawdown protection) ❌
- **Withdrawals** (should NOT trigger drawdown protection) ✅
- **Deposits** (should update peak balance) ✅

When you withdraw funds, the bot sees the balance decrease and thinks you lost money trading, triggering a false drawdown alarm.

## Current Situation

- Peak Balance: $937.86 (set at 13:42)
- You withdrew: $350
- Current Balance: $577.29
- Bot thinks: 38% drawdown (FALSE ALARM!)
- Reality: No trading loss, just a withdrawal

## Immediate Solution

**Restart the bot** to reset the peak balance:

```bash
# Stop the bot (Ctrl+C if running in terminal)
# Then restart it
python test_bot_live.py
```

When the bot restarts:
- Peak balance will reset to current balance: $577.29
- Drawdown calculation will start fresh
- Trading will resume normally

## Best Practices

### Before Making a Withdrawal

1. **Stop the bot** before withdrawing funds
2. **Make your withdrawal** in MT5
3. **Restart the bot** after withdrawal completes
4. Peak will automatically reset to new balance

### After Making a Withdrawal (If Bot Was Running)

1. **Stop the bot immediately**
2. **Restart the bot**
3. Peak resets automatically

### For Deposits

Same process:
1. Stop the bot
2. Make deposit
3. Restart the bot
4. Peak will update to new higher balance

## Why This Happens

The bot's `peak_balance` is stored in memory and only updates when:
- Bot starts (sets to current balance)
- Balance increases above peak (from profitable trading)

It does NOT account for:
- Manual withdrawals (balance decreases, but not from trading)
- Manual deposits (balance increases, but not from trading)

## Future Enhancement Ideas

We could add:
1. **Manual peak reset command** in dashboard
2. **Withdrawal/deposit detection** by checking MT5 deal history
3. **Peak balance persistence** to file (survives restarts)
4. **Configurable drawdown calculation** (daily, weekly, monthly resets)

## For Now

**Just restart the bot whenever you withdraw or deposit funds.**

This is the simplest and most reliable solution until we implement proper withdrawal/deposit handling.

## Summary

Your situation:
- ✅ No trading losses
- ✅ Made a $350 withdrawal
- ✅ Bot triggered false alarm (expected behavior)
- ✅ **Solution: Restart the bot**

After restart:
- Peak: $577.29 (current balance)
- Drawdown: 0%
- Trading: Resumes normally
