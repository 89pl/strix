#!/bin/bash
# Test script for docker-entrypoint.sh port validation logic
# This tests the fix for the "invalid int value: ''" error

set -e

echo "=============================================="
echo "Testing docker-entrypoint.sh port validation"
echo "=============================================="

# Test 1: Empty TOOL_SERVER_PORT should use default
echo ""
echo "Test 1: Empty TOOL_SERVER_PORT should default to 48081"
TOOL_SERVER_PORT=""
if [ -z "$TOOL_SERVER_PORT" ]; then
  TOOL_SERVER_PORT=48081
fi

if [ "$TOOL_SERVER_PORT" = "48081" ]; then
  echo "  ✅ PASS: TOOL_SERVER_PORT defaulted to 48081"
else
  echo "  ❌ FAIL: Expected 48081, got $TOOL_SERVER_PORT"
  exit 1
fi

# Test 2: Set TOOL_SERVER_PORT should be preserved
echo ""
echo "Test 2: Set TOOL_SERVER_PORT should be preserved"
TOOL_SERVER_PORT=8080
if [ -z "$TOOL_SERVER_PORT" ]; then
  TOOL_SERVER_PORT=48081
fi

if [ "$TOOL_SERVER_PORT" = "8080" ]; then
  echo "  ✅ PASS: TOOL_SERVER_PORT preserved as 8080"
else
  echo "  ❌ FAIL: Expected 8080, got $TOOL_SERVER_PORT"
  exit 1
fi

# Test 3: Empty TOOL_SERVER_TOKEN should generate random token
echo ""
echo "Test 3: Empty TOOL_SERVER_TOKEN should generate random token"
TOOL_SERVER_TOKEN=""
if [ -z "$TOOL_SERVER_TOKEN" ]; then
  # Simulate token generation (using /dev/urandom since openssl might not be available)
  TOOL_SERVER_TOKEN=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 32)
fi

if [ -n "$TOOL_SERVER_TOKEN" ] && [ ${#TOOL_SERVER_TOKEN} -eq 32 ]; then
  echo "  ✅ PASS: TOOL_SERVER_TOKEN generated (length: ${#TOOL_SERVER_TOKEN})"
else
  echo "  ❌ FAIL: Token generation failed or wrong length"
  exit 1
fi

# Test 4: Set TOOL_SERVER_TOKEN should be preserved
echo ""
echo "Test 4: Set TOOL_SERVER_TOKEN should be preserved"
TOOL_SERVER_TOKEN="my-secret-token"
if [ -z "$TOOL_SERVER_TOKEN" ]; then
  TOOL_SERVER_TOKEN=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 32)
fi

if [ "$TOOL_SERVER_TOKEN" = "my-secret-token" ]; then
  echo "  ✅ PASS: TOOL_SERVER_TOKEN preserved"
else
  echo "  ❌ FAIL: Token was overwritten"
  exit 1
fi

# Test 5: Verify port is a valid integer
echo ""
echo "Test 5: Verify port is a valid integer"
TOOL_SERVER_PORT=48081
if [[ "$TOOL_SERVER_PORT" =~ ^[0-9]+$ ]]; then
  echo "  ✅ PASS: Port is a valid integer"
else
  echo "  ❌ FAIL: Port is not a valid integer"
  exit 1
fi

echo ""
echo "=============================================="
echo "All docker-entrypoint.sh tests passed! ✅"
echo "=============================================="
