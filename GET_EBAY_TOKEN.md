# How to Get Your eBay Auth Token

To access your eBay orders, you need a **user auth token**. Here are the steps to get one:

## Method 1: Using eBay Developer Console (Recommended)

1. **Go to eBay Developer Console**  
   Visit: https://developer.ebay.com/my/keys

2. **Select Your Application**  
   Click on your existing app or create a new one

3. **Generate User Token**  
   - Click "Generate user token"  
   - Sign in with your eBay seller account
   - Grant permissions to your app
   - Copy the generated token

4. **Add to Environment Variables**
   ```bash
   # For production
   export EBAY_AUTH_TOKEN="your_production_token_here"
   
   # For sandbox  
   export EBAY_SANDBOX_AUTH_TOKEN="your_sandbox_token_here"
   ```
## Testing the Token

Once you have the token set, run:
```bash
make test-api-production
```

You should now see your orders instead of authentication errors!

## Token Permissions

Your token needs these permissions:
- `https://api.ebay.com/ws/api/PrivateData` - to read your orders
- `https://api.ebay.com/ws/api/Sell` - to create shipping labels (for future features)

## Troubleshooting

If you still get auth errors:
1. Double-check the token is correctly set in environment variables
2. Verify the token hasn't expired
3. Make sure you're using the right token for the right environment (sandbox vs production)
4. Check that your app has the necessary scopes/permissions