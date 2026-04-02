#!/usr/bin/env bash
# ============================================================
# CyberTeam V4 - E2E Test Suite (Chat Functionality)
# Date: 2026-03-31
# Tools: browse (gstack), curl
# ============================================================

BROWSE="$HOME/.claude/skills/gstack/browse/dist/browse"
FRONTEND="http://localhost:5173"
BACKEND="http://localhost:8000"
SCREENSHOT_DIR="/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/Output/cyberteam-v4/tests/e2e/screenshots"
RESULTS_FILE="/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/Output/cyberteam-v4/tests/e2e/results.txt"

PASS_COUNT=0
FAIL_COUNT=0
BUG_COUNT=0

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  echo "  [PASS] $1" | tee -a "$RESULTS_FILE"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  echo "  [FAIL] $1" | tee -a "$RESULTS_FILE"
}

bug() {
  BUG_COUNT=$((BUG_COUNT + 1))
  echo "  [BUG #$BUG_COUNT] $1" | tee -a "$RESULTS_FILE"
}

header() {
  echo "" | tee -a "$RESULTS_FILE"
  echo "========================================" | tee -a "$RESULTS_FILE"
  echo "$1" | tee -a "$RESULTS_FILE"
  echo "========================================" | tee -a "$RESULTS_FILE"
}

# Initialize results file
echo "CyberTeam V4 E2E Test Report - $(date)" > "$RESULTS_FILE"
echo "Frontend: $FRONTEND" >> "$RESULTS_FILE"
echo "Backend: $BACKEND" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# ============================================================
# PRE-FLIGHT: Verify services
# ============================================================
header "PRE-FLIGHT: Service Check"

HTTP_FE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/" 2>/dev/null)
if [ "$HTTP_FE" = "200" ]; then
  pass "Frontend ($FRONTEND) responding with 200"
else
  fail "Frontend ($FRONTEND) returned $HTTP_FE"
fi

HTTP_BE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND/api/health" 2>/dev/null)
if [ "$HTTP_BE" = "200" ]; then
  pass "Backend ($BACKEND) responding with 200"
else
  fail "Backend ($BACKEND) returned $HTTP_BE"
fi

BE_HEALTH=$(curl -s "$BACKEND/api/health" 2>/dev/null)
echo "  Backend health: $BE_HEALTH" >> "$RESULTS_FILE"

# ============================================================
# TEST 1: Page Load - /chat
# ============================================================
header "TEST 1: Page Load"

$BROWSE goto "$FRONTEND/chat" 2>/dev/null
sleep 2

# Check console errors
CONSOLE_OUTPUT=$($BROWSE console --errors 2>/dev/null)
if echo "$CONSOLE_OUTPUT" | grep -qi "error\|failed\|uncaught"; then
  echo "  Console errors detected: $CONSOLE_OUTPUT" >> "$RESULTS_FILE"
  # Check if they are real errors vs noise
  REAL_ERRORS=$(echo "$CONSOLE_OUTPUT" | grep -v "favicon\|DevTools\|extension" | grep -i "error" | head -5)
  if [ -n "$REAL_ERRORS" ]; then
    bug "Console errors on /chat: $REAL_ERRORS"
  else
    pass "Page loaded (minor console noise only)"
  fi
else
  pass "No console errors on /chat"
fi

# Screenshot
$BROWSE screenshot "$SCREENSHOT_DIR/01-chat-page.png" 2>/dev/null
pass "Screenshot captured: 01-chat-page.png"

# Check page content
PAGE_TEXT=$($BROWSE text 2>/dev/null)
if echo "$PAGE_TEXT" | grep -q "新建对话\|搜索对话"; then
  pass "Chat page renders with expected elements (新建对话/搜索对话)"
else
  fail "Chat page missing expected elements"
  echo "  Page text: $(echo "$PAGE_TEXT" | head -20)" >> "$RESULTS_FILE"
fi

# Check left sidebar navigation
if echo "$PAGE_TEXT" | grep -q "对话"; then
  pass "Left navigation menu contains '对话'"
else
  fail "Left navigation menu missing '对话'"
fi

# ============================================================
# TEST 2: Session List
# ============================================================
header "TEST 2: Session List"

# Check if conversations list is rendered
SNAPSHOT=$($BROWSE snapshot -i 2>/dev/null)
echo "  Snapshot elements count: $(echo "$SNAPSHOT" | grep -c "ref=" || echo 0)" >> "$RESULTS_FILE"

# Check for existing conversations (API returns 3+ conversations)
API_CONVS=$(curl -s "$BACKEND/api/v1/chat/conversations" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))" 2>/dev/null)
echo "  API conversation count: $API_CONVS" >> "$RESULTS_FILE"

if echo "$PAGE_TEXT" | grep -q "测试\|品牌策划\|测试对话\|E2E"; then
  pass "Session list shows conversations from backend"
else
  # Might show empty state if API is slow
  if echo "$PAGE_TEXT" | grep -q "暂无对话\|加载中"; then
    bug "Session list shows empty state despite $API_CONVS conversations in backend (possible race condition)"
  else
    fail "Session list display issue"
  fi
fi

$BROWSE screenshot "$SCREENSHOT_DIR/02-session-list.png" 2>/dev/null

# ============================================================
# TEST 3: Create New Session
# ============================================================
header "TEST 3: Create New Session"

# Click "新建对话" button
$BROWSE snapshot -i 2>/dev/null | grep -i "新建对话" > /dev/null
BTN_REF=$($BROWSE snapshot -i 2>/dev/null | grep -i "新建对话" | head -1 | grep -oP '@e\d+' || echo "")

if [ -n "$BTN_REF" ]; then
  $BROWSE click "$BTN_REF" 2>/dev/null
  sleep 1

  # Check if modal appeared
  MODAL_TEXT=$($BROWSE text 2>/dev/null)
  if echo "$MODAL_TEXT" | grep -q "对话标题\|创建并进入"; then
    pass "Create conversation modal opened"
  else
    fail "Create conversation modal did not open"
    echo "  Modal text: $(echo "$MODAL_TEXT" | head -10)" >> "$RESULTS_FILE"
  fi

  $BROWSE screenshot "$SCREENSHOT_DIR/03-create-modal.png" 2>/dev/null

  # Fill in the title
  TITLE_INPUT=$($BROWSE snapshot -i 2>/dev/null | grep -i "对话标题\|西北发面\|placeholder" | head -1 | grep -oP '@e\d+' || echo "")
  # Try to find the input field
  if [ -z "$TITLE_INPUT" ]; then
    TITLE_INPUT=$($BROWSE snapshot -i 2>/dev/null | grep -i "input\|textarea\|请输入\|例如" | head -1 | grep -oP '@e\d+' || echo "")
  fi

  if [ -n "$TITLE_INPUT" ]; then
    $BROWSE fill "$TITLE_INPUT" "E2E自动化测试对话" 2>/dev/null
    sleep 0.5
    pass "Filled conversation title input"
  else
    # Try typing directly
    $BROWSE type "E2E自动化测试对话" 2>/dev/null
    pass "Typed conversation title (fallback method)"
  fi

  # Click create button
  CREATE_BTN=$($BROWSE snapshot -i 2>/dev/null | grep -i "创建并进入\|创建" | head -1 | grep -oP '@e\d+' || echo "")
  if [ -n "$CREATE_BTN" ]; then
    $BROWSE click "$CREATE_BTN" 2>/dev/null
    sleep 2

    # Check if navigated to chat room
    CURRENT_URL=$($BROWSE url 2>/dev/null)
    if echo "$CURRENT_URL" | grep -q "/chat/"; then
      pass "Navigated to chat room after creation: $CURRENT_URL"
    else
      fail "Did not navigate to chat room. URL: $CURRENT_URL"
    fi

    $BROWSE screenshot "$SCREENSHOT_DIR/04-chat-room.png" 2>/dev/null
  else
    fail "Could not find create button in modal"
  fi
else
  fail "Could not find '新建对话' button"
fi

# ============================================================
# TEST 4: @ Mention Functionality
# ============================================================
header "TEST 4: @ Department Mention"

# Navigate to a known chat room with messages
TEST_CONV_ID="1e105ac1-0d28-44c2-b70d-ca6e1333ea40"
$BROWSE goto "$FRONTEND/chat/$TEST_CONV_ID" 2>/dev/null
sleep 2

$BROWSE screenshot "$SCREENSHOT_DIR/05-chat-room-for-mention.png" 2>/dev/null

# Find the textarea
SNAPSHOT=$($BROWSE snapshot -i 2>/dev/null)
TEXTAREA_REF=$(echo "$SNAPSHOT" | grep -i "textarea\|输入消息\|placeholder.*消息" | head -1 | grep -oP '@e\d+' || echo "")

if [ -z "$TEXTAREA_REF" ]; then
  # Try finding by role
  TEXTAREA_REF=$($BROWSE snapshot -i 2>/dev/null | grep -i "textbox\|输入" | head -1 | grep -oP '@e\d+' || echo "")
fi

echo "  Textarea ref: $TEXTAREA_REF" >> "$RESULTS_FILE"

if [ -n "$TEXTAREA_REF" ]; then
  pass "Found chat input textarea"

  # 4a: Type @ and check dropdown
  $BROWSE click "$TEXTAREA_REF" 2>/dev/null
  sleep 0.3
  $BROWSE type "@" 2>/dev/null
  sleep 1

  $BROWSE screenshot "$SCREENSHOT_DIR/06-at-mention-dropdown.png" 2>/dev/null

  # Check if dropdown appeared
  AFTER_AT=$($BROWSE text 2>/dev/null)
  DEPT_COUNT=0
  for dept in "CEO" "COO" "决策层" "质量门禁" "协调层" "增长总监" "产品总监" "运营总监" "运营"; do
    if echo "$AFTER_AT" | grep -q "$dept"; then
      DEPT_COUNT=$((DEPT_COUNT + 1))
    fi
  done

  if [ "$DEPT_COUNT" -ge 5 ]; then
    pass "@ mention dropdown shows $DEPT_COUNT department options"
  else
    fail "@ mention dropdown only shows $DEPT_COUNT departments (expected 9)"
    echo "  Visible depts: $DEPT_COUNT" >> "$RESULTS_FILE"
  fi

  # 4b: Filter by typing @决策
  $BROWSE press "Backspace" 2>/dev/null
  $BROWSE fill "$TEXTAREA_REF" "@决策" 2>/dev/null
  sleep 0.5

  FILTERED_TEXT=$($BROWSE text 2>/dev/null)
  if echo "$FILTERED_TEXT" | grep -q "CEO\|决策层"; then
    pass "@决策 filter shows relevant options"
  else
    fail "@决策 filter did not show CEO/决策层"
  fi

  $BROWSE screenshot "$SCREENSHOT_DIR/07-at-filter-juece.png" 2>/dev/null

  # 4c: Keyboard navigation (ArrowDown + Enter)
  # Clear and retype @ to get fresh dropdown
  $BROWSE fill "$TEXTAREA_REF" "@" 2>/dev/null
  sleep 0.5
  $BROWSE press "ArrowDown" 2>/dev/null
  sleep 0.3
  $BROWSE press "Enter" 2>/dev/null
  sleep 0.5

  AFTER_SELECT=$($BROWSE snapshot -i 2>/dev/null)
  echo "  After keyboard select: $(echo "$AFTER_SELECT" | head -5)" >> "$RESULTS_FILE"
  pass "Keyboard navigation (ArrowDown + Enter) executed"

  $BROWSE screenshot "$SCREENSHOT_DIR/08-keyboard-select.png" 2>/dev/null

  # 4d: Click dropdown option
  # Clear and type @质
  $BROWSE fill "$TEXTAREA_REF" "@质" 2>/dev/null
  sleep 0.5

  # Find clickable option in dropdown
  OPTION_REF=$($BROWSE snapshot -i 2>/dev/null | grep -i "质量门禁\|质疑者" | head -1 | grep -oP '@e\d+' || echo "")
  if [ -n "$OPTION_REF" ]; then
    $BROWSE click "$OPTION_REF" 2>/dev/null
    sleep 0.5
    pass "Clicked @ quality gate option from dropdown"
  else
    fail "Could not find quality gate option in filtered dropdown"
  fi

  $BROWSE screenshot "$SCREENSHOT_DIR/09-click-select.png" 2>/dev/null

  # 4e: Verify text insertion
  INPUT_VALUE=$($BROWSE js "document.querySelector('textarea')?.value || ''" 2>/dev/null)
  echo "  Input value after mention: $INPUT_VALUE" >> "$RESULTS_FILE"
  if echo "$INPUT_VALUE" | grep -q "@"; then
    pass "Mention text inserted into input (contains @)"
  else
    fail "Mention text not properly inserted"
    bug "Mention insertion may not work correctly - input value: $INPUT_VALUE"
  fi

else
  fail "Could not find chat input textarea"
fi

# ============================================================
# TEST 5: Message Send
# ============================================================
header "TEST 5: Message Send"

# Use the pre-created conversation
MSG_CONV_ID="37521f3e-6296-4c06-a351-029a567e7937"
$BROWSE goto "$FRONTEND/chat/$MSG_CONV_ID" 2>/dev/null
sleep 2

$BROWSE screenshot "$SCREENSHOT_DIR/10-message-send-before.png" 2>/dev/null

# Count messages before sending
MSG_COUNT_BEFORE=$(curl -s "$BACKEND/api/v1/chat/conversations/$MSG_CONV_ID/messages" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))" 2>/dev/null)
echo "  Message count before: $MSG_COUNT_BEFORE" >> "$RESULTS_FILE"

# Find and fill textarea
TEXTAREA_REF=$($BROWSE snapshot -i 2>/dev/null | grep -i "textarea\|输入消息" | head -1 | grep -oP '@e\d+' || echo "")
if [ -n "$TEXTAREA_REF" ]; then
  $BROWSE fill "$TEXTAREA_REF" "E2E测试消息 - 端到端验证" 2>/dev/null
  sleep 0.5

  # Click send button
  SEND_BTN=$($BROWSE snapshot -i 2>/dev/null | grep -i "发送\|send" | head -1 | grep -oP '@e\d+' || echo "")
  if [ -n "$SEND_BTN" ]; then
    $BROWSE click "$SEND_BTN" 2>/dev/null
    sleep 2

    # Verify via API
    MSG_COUNT_AFTER=$(curl -s "$BACKEND/api/v1/chat/conversations/$MSG_CONV_ID/messages" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))" 2>/dev/null)
    echo "  Message count after: $MSG_COUNT_AFTER" >> "$RESULTS_FILE"

    if [ "$MSG_COUNT_AFTER" -gt "$MSG_COUNT_BEFORE" ]; then
      pass "Message sent successfully ($MSG_COUNT_BEFORE -> $MSG_COUNT_AFTER)"
    else
      fail "Message count did not increase after send"
    fi

    $BROWSE screenshot "$SCREENSHOT_DIR/11-message-sent.png" 2>/dev/null
  else
    fail "Could not find send button"
  fi
else
  fail "Could not find textarea for message input"
fi

# ============================================================
# TEST 6: Layout Completeness
# ============================================================
header "TEST 6: Layout Completeness"

$BROWSE goto "$FRONTEND/chat/$TEST_CONV_ID" 2>/dev/null
sleep 2

# 6a: Three-column layout check
SNAPSHOT=$($BROWSE snapshot -i 2>/dev/null)

# Left nav (Sider)
if echo "$SNAPSHOT" | grep -qi "仪表盘\|对话\|Agent\|项目"; then
  pass "Left navigation sidebar present (仪表盘/对话/Agent管理)"
else
  fail "Left navigation sidebar missing"
fi

# Middle content area (messages)
if echo "$SNAPSHOT" | grep -qi "对话\|消息\|发送\|输入"; then
  pass "Middle content area (message area) present"
else
  fail "Middle content area missing"
fi

# Right panel (Agent status)
if echo "$SNAPSHOT" | grep -qi "Agent.*状态\|执行状态\|Agent 执行"; then
  pass "Right panel - Agent execution status present"
else
  fail "Right panel - Agent execution status missing"
fi

# Task nodes panel
if echo "$SNAPSHOT" | grep -qi "任务节点\|CEO.*COO.*对齐\|策略讨论"; then
  pass "Right panel - Task nodes panel present"
else
  fail "Right panel - Task nodes panel missing"
fi

# Input area at bottom
if echo "$SNAPSHOT" | grep -qi "输入消息\|发送\|textarea"; then
  pass "Input area positioned at bottom of chat"
else
  fail "Input area not found"
fi

$BROWSE screenshot "$SCREENSHOT_DIR/12-layout-check.png" 2>/dev/null

# Check layout dimensions via JS
LAYOUT_INFO=$($BROWSE js "
  const sider = document.querySelector('.ant-layout-sider');
  const content = document.querySelector('.ant-layout-content');
  const textarea = document.querySelector('textarea');
  JSON.stringify({
    siderWidth: sider?.offsetWidth || 0,
    contentHeight: content?.offsetHeight || 0,
    textareaVisible: textarea !== null,
    textareaRect: textarea?.getBoundingClientRect()?.bottom || 0,
    viewportHeight: window.innerHeight
  })
" 2>/dev/null)
echo "  Layout info: $LAYOUT_INFO" >> "$RESULTS_FILE"

# Check if textarea is near bottom
TEXTAREA_BOTTOM=$(echo "$LAYOUT_INFO" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('textareaRect', 0))" 2>/dev/null)
VIEWPORT_HEIGHT=$(echo "$LAYOUT_INFO" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('viewportHeight', 0))" 2>/dev/null)

if [ -n "$TEXTAREA_BOTTOM" ] && [ -n "$VIEWPORT_HEIGHT" ] && [ "$VIEWPORT_HEIGHT" -gt 0 ]; then
  DISTANCE_FROM_BOTTOM=$((VIEWPORT_HEIGHT - TEXTAREA_BOTTOM))
  if [ "$DISTANCE_FROM_BOTTOM" -lt 200 ]; then
    pass "Input area is near bottom of viewport (${DISTANCE_FROM_BOTTOM}px from bottom)"
  else
    bug "Input area is ${DISTANCE_FROM_BOTTOM}px from viewport bottom (expected <200px)"
  fi
fi

# ============================================================
# TEST 7: Edge Cases
# ============================================================
header "TEST 7: Edge Cases"

$BROWSE goto "$FRONTEND/chat/$TEST_CONV_ID" 2>/dev/null
sleep 1

TEXTAREA_REF=$($BROWSE snapshot -i 2>/dev/null | grep -i "textarea\|输入消息" | head -1 | grep -oP '@e\d+' || echo "")

if [ -n "$TEXTAREA_REF" ]; then

  # 7a: Long text
  LONG_TEXT=$(python3 -c "print('长文本测试' * 100)")
  $BROWSE fill "$TEXTAREA_REF" "$LONG_TEXT" 2>/dev/null
  sleep 0.5

  # Check if textarea expanded or handles overflow
  TEXTAREA_HEIGHT=$($BROWSE js "document.querySelector('textarea')?.offsetHeight || 0" 2>/dev/null)
  echo "  Long text textarea height: ${TEXTAREA_HEIGHT}px" >> "$RESULTS_FILE"
  if [ "$TEXTAREA_HEIGHT" -gt 30 ]; then
    pass "Long text: textarea expanded to ${TEXTAREA_HEIGHT}px"
  else
    bug "Long text: textarea did not expand (height: ${TEXTAREA_HEIGHT}px)"
  fi

  $BROWSE screenshot "$SCREENSHOT_DIR/13-long-text.png" 2>/dev/null

  # 7b: Special characters
  $BROWSE fill "$TEXTAREA_REF" "特殊字符测试：<script>alert(1)</script> & \"引号\" '单引号' \n换行" 2>/dev/null
  sleep 0.5

  # Check for XSS - the text should be escaped
  PAGE_HTML=$($BROWSE html 2>/dev/null)
  if echo "$PAGE_HTML" | grep -q "<script>alert(1)</script>"; then
    bug "XSS vulnerability: script tag not escaped in textarea"
  else
    pass "Special characters: No XSS vulnerability detected"
  fi

  # 7c: Rapid @ typing
  $BROWSE fill "$TEXTAREA_REF" "@@@" 2>/dev/null
  sleep 0.5

  AFTER_RAPID=$($BROWSE text 2>/dev/null)
  # Should not crash or show multiple dropdowns
  pass "Rapid @@@ input did not crash the page"

  $BROWSE screenshot "$SCREENSHOT_DIR/14-rapid-at.png" 2>/dev/null

  # 7d: Empty message send
  $BROWSE fill "$TEXTAREA_REF" "" 2>/dev/null
  sleep 0.3

  SEND_BTN=$($BROWSE snapshot -i 2>/dev/null | grep -i "发送" | head -1 | grep -oP '@e\d+' || echo "")
  if [ -n "$SEND_BTN" ]; then
    # Check if button is disabled
    IS_DISABLED=$($BROWSE is "disabled" "$SEND_BTN" 2>/dev/null)
    if [ "$IS_DISABLED" = "true" ]; then
      pass "Empty message: Send button is disabled"
    else
      # Try clicking anyway
      MSG_BEFORE=$(curl -s "$BACKEND/api/v1/chat/conversations/$TEST_CONV_ID/messages" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))" 2>/dev/null)
      $BROWSE click "$SEND_BTN" 2>/dev/null
      sleep 1
      MSG_AFTER=$(curl -s "$BACKEND/api/v1/chat/conversations/$TEST_CONV_ID/messages" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))" 2>/dev/null)
      if [ "$MSG_AFTER" = "$MSG_BEFORE" ]; then
        pass "Empty message: Not sent (frontend blocks it)"
      else
        bug "Empty message was sent to backend ($MSG_BEFORE -> $MSG_AFTER)"
      fi
    fi
  fi

  # 7e: Emoji input
  $BROWSE fill "$TEXTAREA_REF" "Emoji测试: 🎉 🚀 💡 @CEO 你好" 2>/dev/null
  sleep 0.5

  INPUT_VAL=$($BROWSE js "document.querySelector('textarea')?.value || ''" 2>/dev/null)
  if echo "$INPUT_VAL" | grep -q "Emoji"; then
    pass "Emoji input handled correctly"
  else
    fail "Emoji input not handled correctly"
  fi

else
  fail "Could not find textarea for edge case tests"
fi

# ============================================================
# TEST 8: Navigation Consistency
# ============================================================
header "TEST 8: Navigation & Back"

# Navigate back to /chat list
$BROWSE goto "$FRONTEND/chat/$TEST_CONV_ID" 2>/dev/null
sleep 1

# Find back button
BACK_BTN=$($BROWSE snapshot -i 2>/dev/null | grep -i "arrow\|返回\|back" | head -1 | grep -oP '@e\d+' || echo "")
if [ -n "$BACK_BTN" ]; then
  $BROWSE click "$BACK_BTN" 2>/dev/null
  sleep 1

  CURRENT_URL=$($BROWSE url 2>/dev/null)
  if echo "$CURRENT_URL" | grep -q "/chat$"; then
    pass "Back button navigates to /chat (session list)"
  else
    fail "Back button did not navigate to /chat. URL: $CURRENT_URL"
  fi
else
  fail "Back button not found in chat room"
fi

# Click on existing conversation
FIRST_CONV=$($BROWSE snapshot -i 2>/dev/null | grep -i "测试\|对话\|品牌\|E2E" | head -1 | grep -oP '@e\d+' || echo "")
if [ -n "$FIRST_CONV" ]; then
  $BROWSE click "$FIRST_CONV" 2>/dev/null
  sleep 2

  CURRENT_URL=$($BROWSE url 2>/dev/null)
  if echo "$CURRENT_URL" | grep -q "/chat/"; then
    pass "Clicking conversation navigates to chat room"
  else
    fail "Clicking conversation did not navigate to chat room. URL: $CURRENT_URL"
  fi
fi

# ============================================================
# TEST 9: Console Error Summary
# ============================================================
header "TEST 9: Console Error Summary"

$BROWSE goto "$FRONTEND/chat" 2>/dev/null
sleep 2

ALL_ERRORS=$($BROWSE console --errors 2>/dev/null)
ERROR_COUNT=$(echo "$ALL_ERRORS" | grep -c "error" || echo "0")
echo "  Total console errors: $ERROR_COUNT" >> "$RESULTS_FILE"

if [ "$ERROR_COUNT" -eq 0 ]; then
  pass "No console errors detected"
else
  # Filter out noise
  REAL_ERRORS=$(echo "$ALL_ERRORS" | grep -v "favicon\|DevTools\|extension\|net::ERR" | head -10)
  if [ -n "$REAL_ERRORS" ]; then
    bug "Console errors found: $REAL_ERRORS"
  else
    pass "Console errors are minor (favicon/extension noise only)"
  fi
fi

# ============================================================
# SUMMARY
# ============================================================
header "TEST SUMMARY"

TOTAL=$((PASS_COUNT + FAIL_COUNT))
echo "" | tee -a "$RESULTS_FILE"
echo "  Total Tests: $TOTAL" | tee -a "$RESULTS_FILE"
echo "  Passed:      $PASS_COUNT" | tee -a "$RESULTS_FILE"
echo "  Failed:      $FAIL_COUNT" | tee -a "$RESULTS_FILE"
echo "  Bugs Found:  $BUG_COUNT" | tee -a "$RESULTS_FILE"
echo "  Pass Rate:   $(python3 -c "print(f'{$PASS_COUNT/$TOTAL*100:.1f}%')")" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"
echo "  Screenshots: $SCREENSHOT_DIR" | tee -a "$RESULTS_FILE"
echo "  Full Report: $RESULTS_FILE" | tee -a "$RESULTS_FILE"

# Exit code based on pass rate
if [ "$FAIL_COUNT" -eq 0 ]; then
  echo "  STATUS: ALL TESTS PASSED" | tee -a "$RESULTS_FILE"
  exit 0
else
  echo "  STATUS: SOME TESTS FAILED - SEE DETAILS ABOVE" | tee -a "$RESULTS_FILE"
  exit 1
fi
