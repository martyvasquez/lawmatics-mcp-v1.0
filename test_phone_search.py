#!/usr/bin/env python3
"""Test script to demonstrate phone number search functionality.

This script shows how the MCP server would handle the request:
"Find all matters associated with the phone number 714-917-5140"

NOTE: This requires a valid LAWMATICS_API_KEY in your .env file.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.tools.search import search_contacts, search_matters

async def test_phone_search():
    """Test finding matters by phone number."""
    phone_number = "714-917-5140"

    print(f"\n{'='*70}")
    print(f"TESTING: Find all matters associated with phone: {phone_number}")
    print(f"{'='*70}\n")

    # Check if API key is set
    api_key = os.getenv("LAWMATICS_API_KEY")
    if not api_key or api_key == "test_key_placeholder":
        print("⚠️  WARNING: LAWMATICS_API_KEY not set or using placeholder")
        print("To test with real API:")
        print("1. Get your API key from Lawmatics (Settings → API)")
        print("2. Update LAWMATICS_API_KEY in .env file")
        print("3. Run this script again\n")
        print("=" * 70)
        print("SIMULATED WORKFLOW (what would happen with valid API key):")
        print("=" * 70)
        print("\nSTEP 1: Search for contacts with phone: 714-917-5140")
        print("  Tool: search_contacts")
        print("  Parameters: {phone: '714-917-5140'}")
        print("  Expected: List of contacts matching this phone number")
        print("\nSTEP 2: For each contact found:")
        print("  - Extract contact_id")
        print("  - Display contact name, email, status")
        print("\nSTEP 3: Search for matters associated with each contact")
        print("  Tool: search_matters")
        print("  Parameters: {contact_id: '<each_contact_id>'}")
        print("  Expected: List of matters for each contact")
        print("\nSTEP 4: Display summary:")
        print("  - Total contacts found with this phone")
        print("  - Total matters associated")
        print("  - Matter details (name, status, practice area)")
        print("\n" + "=" * 70)
        return

    try:
        # Step 1: Search for contacts by phone
        print("STEP 1: Searching for contacts with phone:", phone_number)
        print("-" * 70)

        contacts_result = await search_contacts(phone=phone_number)

        # Handle both list and dict responses
        if isinstance(contacts_result, list):
            contacts = contacts_result
        else:
            contacts = contacts_result.get("data", contacts_result.get("results", []))

        print(f"Found {len(contacts)} contact(s)\n")

        if not contacts:
            print("No contacts found with this phone number.")
            return

        # Step 2: Display contacts and find their matters
        all_matters = []

        for idx, contact in enumerate(contacts, 1):
            contact_id = contact.get("id")
            contact_name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
            contact_email = contact.get("email", "N/A")
            contact_status = contact.get("status", "N/A")

            print(f"\nContact {idx}:")
            print(f"  Name:   {contact_name}")
            print(f"  Email:  {contact_email}")
            print(f"  Status: {contact_status}")
            print(f"  ID:     {contact_id}")

            # Step 3: Search for matters for this contact
            if contact_id:
                print(f"\n  Searching for matters associated with {contact_name}...")
                print("  " + "-" * 66)

                matters_result = await search_matters(contact_id=contact_id)

                # Handle both list and dict responses
                if isinstance(matters_result, list):
                    matters = matters_result
                else:
                    matters = matters_result.get("data", matters_result.get("results", []))

                print(f"  Found {len(matters)} matter(s)\n")

                if matters:
                    for matter in matters:
                        matter_name = matter.get("name", "Unnamed Matter")
                        matter_status = matter.get("status", "N/A")
                        practice_area = matter.get("practice_area", "N/A")

                        print(f"    • {matter_name}")
                        print(f"      Status: {matter_status}")
                        print(f"      Practice Area: {practice_area}")
                        print()

                        all_matters.append({
                            "contact": contact_name,
                            "matter": matter_name,
                            "status": matter_status,
                            "practice_area": practice_area
                        })
                else:
                    print("    No matters found for this contact.\n")

        # Step 4: Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Phone Number: {phone_number}")
        print(f"Total Contacts Found: {len(contacts)}")
        print(f"Total Matters Found: {len(all_matters)}")

        if all_matters:
            print("\nAll Matters Associated with this Phone Number:")
            print("-" * 70)
            for matter in all_matters:
                print(f"• {matter['matter']}")
                print(f"  Contact: {matter['contact']}")
                print(f"  Status: {matter['status']}")
                print(f"  Practice Area: {matter['practice_area']}")
                print()

        print("=" * 70)

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("Make sure your LAWMATICS_API_KEY is set correctly in .env")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("LAWMATICS MCP SERVER - PHONE SEARCH TEST")
    print("=" * 70)
    asyncio.run(test_phone_search())
    print("\n✅ Test completed!\n")
