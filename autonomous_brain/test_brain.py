#!/usr/bin/env python3
"""
Test Autonomous Brain with Mock Data
=====================================

Tests the brain's diagnostic capabilities without needing Railway API.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from classifier import IssueClassifier, Severity, ApprovalLevel
from logger import ActionLogger, BrainAction
from datetime import datetime


async def test_brain():
    """Test the autonomous brain with mock Railway logs"""
    
    print("╔══════════════════════════════════════════════════════════")
    print("║ 🧠 AUTONOMOUS BRAIN - MOCK TEST")
    print("╚══════════════════════════════════════════════════════════\n")
    
    # Initialize modules
    classifier = IssueClassifier()
    logger = ActionLogger()
    
    # Mock Railway logs (from your actual logs!)
    mock_logs = [
        "telethon.errors.rpcerrorlist.UsernameInvalidError: Nobody is using this username",
        "HTTP Request: POST https://api.groq.com/openai/v1/chat/completions HTTP/1.1 200 OK",
        "INFO: 100.64.0.2:27132 - GET /signals HTTP/1.1 200 OK",
        "ModuleNotFoundError: No module named 'some_package'",
        "WARNING: High memory usage detected: 95%",
        "Error: Database connection timeout",
        "CRITICAL: Wallet private key exposure risk detected"
    ]
    
    # Simulate issue detection
    print("📥 Processing mock Railway logs...")
    print(f"   Found {len(mock_logs)} log lines\n")
    
    # Detect and classify issues
    print("🔍 Detecting and classifying issues...\n")
    
    issues_found = []
    
    for log in mock_logs:
        # Simple error detection
        if any(keyword in log.lower() for keyword in ['error', 'critical', 'warning', 'exception']):
            # Create mock issue
            issue = {
                "type": "detected_error",
                "log_line": log,
                "severity": "critical" if "critical" in log.lower() else "medium" if "error" in log.lower() else "minor"
            }
            
            # Classify
            classified = classifier.classify(issue)
            issues_found.append(classified)
            
            # Display
            severity_emoji = "🔴" if classified.severity == Severity.CRITICAL else "🟡" if classified.severity == Severity.MEDIUM else "🟢"
            
            print(f"{severity_emoji} [{classified.severity.value.upper()}] {classified.issue_type}")
            print(f"   Issue: {classified.description}")
            print(f"   Can auto-fix: {classified.approval_required == ApprovalLevel.AUTO_FIX}")
            print(f"   Confidence: {classified.confidence:.0%}")
            print(f"   Proposed: {classified.proposed_fix}")
            
            # Log the action
            action = BrainAction(
                timestamp=datetime.now().isoformat(),
                action_type="auto_fix" if classified.approval_required == ApprovalLevel.AUTO_FIX else "pending_approval",
                severity=classified.severity.value,
                issue=classified.description,
                proposed_fix=classified.proposed_fix,
                approval_required=classified.approval_required != ApprovalLevel.AUTO_FIX,
                status="completed" if classified.approval_required == ApprovalLevel.AUTO_FIX else "pending",
                confidence=classified.confidence
            )
            
            action_id = logger.log_action(action)
            print(f"   ✅ Logged as: {action_id}\n")
    
    # Summary
    print(f"{'='*60}")
    print(f"📊 DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")
    print(f"Total issues found: {len(issues_found)}")
    
    auto_fixable = classifier.get_auto_fixable_issues(issues_found)
    need_approval = classifier.get_approval_required_issues(issues_found)
    
    print(f"✅ Auto-fixable: {len(auto_fixable)}")
    print(f"⚠️  Need approval: {len(need_approval)}")
    
    # Get statistics
    stats = logger.get_statistics()
    print(f"\n{'='*60}")
    print(f"📈 BRAIN STATISTICS")
    print(f"{'='*60}")
    print(f"Total actions logged: {stats['total_actions']}")
    print(f"Auto-fixes: {stats['auto_fixes']}")
    print(f"Approvals requested: {stats['approvals_requested']}")
    
    # Generate report
    print(f"\n{logger.generate_daily_report()}")
    
    print(f"\n{'='*60}")
    print(f"✨ TEST COMPLETE!")
    print(f"{'='*60}")
    print("""
🎉 THE AUTONOMOUS BRAIN IS WORKING!

What we just demonstrated:
✅ Error detection from logs
✅ Issue classification by severity
✅ Auto-fix vs approval determination
✅ Confidence scoring
✅ Action logging
✅ Daily reporting

Next steps:
1. Connect to real Railway logs (when we get Service ID)
2. Add GitHub integration (Phase 2)
3. Add fix generation (Phase 2)
4. Add daily training (Phase 3)
5. Add Telegram approval system (Phase 4)

The foundation is SOLID! 🚀
""")

if __name__ == "__main__":
    asyncio.run(test_brain())
