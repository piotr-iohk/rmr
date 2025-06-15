#!/bin/bash

set -e

RMR=$1  # Reduce Margin Ratio
IMR=$2  # Initial Margin Ratio
MMR=$3  # Maintenance Margin Ratio

CHAIN_ID="injective-1"
PASSPHRASE="12345678"

# Default INJHOME to current directory if not set
if [ -z "$INJHOME" ]; then
  INJHOME="$(pwd)/.injectived"
  echo "INJHOME not set, defaulting to current directory: $INJHOME"
fi

# One time setup, you will not need to run this again
echo "Setup USDT metadata"
yes $PASSPHRASE | injectived tx gov submit-proposal usdt_proposal.json --from testcandidate --chain-id injective-1 --gas-prices 500000000inj --gas 10000000 --yes
sleep 5 # Depending on your local machine, block time may be different, so we sleep for 5 seconds to ensure the txn is included in the next block
yes $PASSPHRASE | injectived tx gov vote 1 yes --from val --chain-id $CHAIN_ID --gas-prices 500000000inj --gas 10000000 --yes
sleep 15 # Voting period is 15 seconds, so we sleep for 15 seconds to ensure the proposal is passed

echo "Setting up perp market"
# This submits a proposal that if passed, allows the symbols TST to receive price feeds from a price feed oracle in terms of USDT
yes $PASSPHRASE | injectived tx oracle grant-price-feeder-privilege-proposal TST USDT inj158ucxjzr6ccrlpmz8z05wylu8tr5eueqang232 --title "Grant price feeder privilege for TST" --description "Grant price feeder privilege for TST" --deposit 100000000000000000000inj --from testcandidate --chain-id $CHAIN_ID --gas-prices 500000000inj --gas 10000000 --yes 
sleep 5

# This votes yes on the proposal from a validator wallet ensuring it has sufficient votes to pass
yes $PASSPHRASE | injectived tx gov vote 2 yes --from val --chain-id $CHAIN_ID --gas-prices 500000000inj --gas 10000000 --yes 
sleep 15

# This relays the price feed from the oracle to the chain
yes $PASSPHRASE | injectived tx oracle relay-price-feed-price TST USDT 15 --from testcandidate --chain-id $CHAIN_ID --gas-prices 500000000inj --gas 10000000 --yes 
sleep 5

# This creates the insurance fund for the perp market
yes $PASSPHRASE | injectived tx insurance create-insurance-fund --ticker "TST/USDT PERP" --quote-denom peggy0xdAC17F958D2ee523a2206206994597C13D831ec7 --oracle-base TST --oracle-quote USDT --oracle-type pricefeed --expiry -1 --initial-deposit 1000peggy0xdAC17F958D2ee523a2206206994597C13D831ec7 --from testcandidate --chain-id $CHAIN_ID --gas-prices 500000000inj --gas 10000000 --yes 
sleep 5

# This submits a proposal to launch the perp market
echo "Submitting proposal to launch TST/USDT PERP market"
yes $PASSPHRASE | injectived tx exchange propose-perpetual-market --ticker "TST/USDT PERP" --oracle-type pricefeed --oracle-base "TST" --oracle-quote USDT --quote-denom peggy0xdAC17F958D2ee523a2206206994597C13D831ec7 --initial-margin-ratio $IMR --maintenance-margin-ratio $MMR --reduce-margin-ratio $RMR --maker-fee-rate 0.0001 --taker-fee-rate 0.002 --min-notional 1 --oracle-scale-factor 0 --min-price-tick-size 0.01 --min-quantity-tick-size 0.01 --admin inj158ucxjzr6ccrlpmz8z05wylu8tr5eueqang232 --admin-permissions 64 --title "TST/USDT PERP MARKET LAUNCH" --description "TST/USDT PERP MARKET LAUNCH" --deposit "100000000000000000000inj" --from testcandidate --chain-id $CHAIN_ID --gas-prices 500000000inj --gas 10000000 --yes
sleep 5

# This votes yes on the proposal from a validator wallet ensuring it has sufficient votes to pass
yes $PASSPHRASE | injectived tx gov vote 3 yes --from val --chain-id $CHAIN_ID --gas-prices 500000000inj --gas 10000000 --yes 
sleep 15

echo "Setup complete"
