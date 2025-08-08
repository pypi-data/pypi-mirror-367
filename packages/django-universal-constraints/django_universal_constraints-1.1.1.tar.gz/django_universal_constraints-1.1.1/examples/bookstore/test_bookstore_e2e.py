"""
End-to-End Test for Bookstore Universal Constraints Demo

This single comprehensive test demonstrates how all constraint types work together
in a realistic bookstore scenario. No test isolation needed - just one continuous
story that shows constraint validation in action.
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_project.settings')
django.setup()

from books.models import Author, Book
from inventory.models import Location, Stock
from customers.models import Customer, Order


class BookstoreE2ETest(TestCase):
    """
    Comprehensive E2E test demonstrating universal constraints in action.
    
    This test tells the story of a bookstore operation, showing how constraints
    protect data integrity across all models and databases.
    """
    
    # Allow access to both databases for multi-database testing
    databases = ['default', 'second_database']
    
    def test_complete_bookstore_workflow(self):
        """
        Complete bookstore workflow demonstrating all constraint types:
        - Conditional constraints (Author emails, Stock records)
        - Non-conditional constraints (Book ISBNs, Location codes)
        - unique_together constraints (Book title+author, Customer data, Orders)
        """
        
        print("\n" + "="*60)
        print("🏪 BOOKSTORE E2E TEST: Universal Constraints in Action")
        print("="*60)
        
        # ================================================================
        # PHASE 1: AUTHOR MANAGEMENT (Conditional Constraints)
        # ================================================================
        print("\n📚 PHASE 1: Author Management (Conditional Constraints)")
        print("-" * 50)
        
        # ✅ Create active authors with unique emails
        print("✅ Creating active authors with unique emails...")
        author1 = Author.objects.create(
            name="J.K. Rowling",
            email="jk.rowling@example.com",
            is_active=True
        )
        author2 = Author.objects.create(
            name="Stephen King",
            email="stephen.king@example.com", 
            is_active=True
        )
        print(f"   Created: {author1}")
        print(f"   Created: {author2}")
        
        # ❌ Try to create duplicate active author email (should fail)
        print("\n❌ Trying to create duplicate active author email...")
        try:
            duplicate_author = Author(
                name="Fake J.K. Rowling",
                email="jk.rowling@example.com",  # Same email as author1
                is_active=True
            )
            duplicate_author.save()
            self.fail("Should have failed due to unique active author email constraint")
        except (ValidationError, IntegrityError) as e:
            print(f"   ✅ CORRECTLY BLOCKED: {type(e).__name__}")
            print(f"   Constraint working: Active authors must have unique emails")
        
        # ✅ Deactivate author, then create new author with same email (should work)
        print("\n✅ Deactivating author1, then creating new author with same email...")
        author1.is_active = False
        author1.save()
        print(f"   Deactivated: {author1}")
        
        new_author = Author.objects.create(
            name="New Author with Reused Email",
            email="jk.rowling@example.com",  # Same email, but original is inactive
            is_active=True
        )
        print(f"   ✅ SUCCESS: {new_author}")
        print("   Constraint working: Only ACTIVE authors need unique emails")
        
        # ================================================================
        # PHASE 2: BOOK MANAGEMENT (Non-conditional + unique_together)
        # ================================================================
        print("\n\n📖 PHASE 2: Book Management (Non-conditional + unique_together)")
        print("-" * 60)
        
        # ✅ Create books with unique ISBNs
        print("✅ Creating books with unique ISBNs...")
        book1 = Book.objects.create(
            title="Harry Potter and the Philosopher's Stone",
            isbn="978-0-7475-3269-9",
            author=new_author  # Using the new active author
        )
        book2 = Book.objects.create(
            title="The Shining",
            isbn="978-0-385-12167-5",
            author=author2
        )
        print(f"   Created: {book1}")
        print(f"   Created: {book2}")
        
        # ❌ Try duplicate ISBN (should fail)
        print("\n❌ Trying to create book with duplicate ISBN...")
        try:
            duplicate_isbn_book = Book(
                title="Different Title",
                isbn="978-0-7475-3269-9",  # Same ISBN as book1
                author=author2
            )
            duplicate_isbn_book.save()
            self.fail("Should have failed due to unique ISBN constraint")
        except (ValidationError, IntegrityError) as e:
            print(f"   ✅ CORRECTLY BLOCKED: {type(e).__name__}")
            print("   Constraint working: All ISBNs must be unique")
        
        # ✅ Create books with same title by different authors (should work)
        print("\n✅ Creating books with same title by different authors...")
        book3 = Book.objects.create(
            title="The Stand",  # Same title we'll use for both
            isbn="978-0-385-19957-9",
            author=author2
        )
        book4 = Book.objects.create(
            title="The Stand",  # Same title, different author
            isbn="978-1-234-56789-0",
            author=new_author  # Different author
        )
        print(f"   ✅ SUCCESS: {book3}")
        print(f"   ✅ SUCCESS: {book4}")
        print("   Constraint working: Same title OK if different authors")
        
        # ❌ Try same title + author combination (should fail via unique_together)
        print("\n❌ Trying same title + author combination...")
        try:
            duplicate_title_author = Book(
                title="The Stand",  # Same title as book3
                isbn="978-9-876-54321-0",
                author=author2  # Same author as book3
            )
            duplicate_title_author.save()
            self.fail("Should have failed due to unique_together constraint")
        except (ValidationError, IntegrityError) as e:
            print(f"   ✅ CORRECTLY BLOCKED: {type(e).__name__}")
            print("   Constraint working: Title + Author must be unique together")
        
        # ================================================================
        # PHASE 3: INVENTORY MANAGEMENT (Non-conditional + Conditional)
        # ================================================================
        print("\n\n📦 PHASE 3: Inventory Management (Multi-Database)")
        print("-" * 50)
        
        # ✅ Create locations with unique codes
        print("✅ Creating warehouse locations with unique codes...")
        location1 = Location.objects.create(
            name="Main Warehouse",
            code="MW01"
        )
        location2 = Location.objects.create(
            name="Secondary Warehouse", 
            code="SW01"
        )
        print(f"   Created: {location1}")
        print(f"   Created: {location2}")
        
        # ❌ Try duplicate location codes (should fail)
        print("\n❌ Trying to create location with duplicate code...")
        try:
            duplicate_location = Location(
                name="Fake Warehouse",
                code="MW01"  # Same code as location1
            )
            duplicate_location.save()
            self.fail("Should have failed due to unique location code constraint")
        except (ValidationError, IntegrityError) as e:
            print(f"   ✅ CORRECTLY BLOCKED: {type(e).__name__}")
            print("   Constraint working: Location codes must be unique")
        
        # ✅ Create active stock records
        print("\n✅ Creating active stock records...")
        stock1 = Stock.objects.create(
            book_id=book1.id,
            book_title=book1.title,
            location=location1,
            quantity=50,
            is_active=True
        )
        stock2 = Stock.objects.create(
            book_id=book2.id,
            book_title=book2.title,
            location=location2,
            quantity=25,
            is_active=True
        )
        print(f"   Created: {stock1}")
        print(f"   Created: {stock2}")
        
        # ❌ Try duplicate active stock for same book+location (should fail)
        print("\n❌ Trying duplicate active stock for same book+location...")
        try:
            duplicate_stock = Stock(
                book_id=book1.id,  # Same book as stock1
                book_title=book1.title,
                location=location1,  # Same location as stock1
                quantity=100,
                is_active=True  # Both active - should conflict
            )
            duplicate_stock.save()
            self.fail("Should have failed due to unique active stock constraint")
        except (ValidationError, IntegrityError) as e:
            print(f"   ✅ CORRECTLY BLOCKED: {type(e).__name__}")
            print("   Constraint working: Only one active stock per book+location")
        
        # ✅ Deactivate stock, create new active stock (should work)
        print("\n✅ Deactivating stock1, then creating new active stock...")
        stock1.is_active = False
        stock1.save()
        print(f"   Deactivated: {stock1}")
        
        new_stock = Stock.objects.create(
            book_id=book1.id,  # Same book+location as deactivated stock1
            book_title=book1.title,
            location=location1,
            quantity=75,
            is_active=True
        )
        print(f"   ✅ SUCCESS: {new_stock}")
        print("   Constraint working: Only ACTIVE stock records must be unique")
        
        # ================================================================
        # PHASE 4: CUSTOMER MANAGEMENT (unique_together constraints)
        # ================================================================
        print("\n\n👥 PHASE 4: Customer Management (unique_together)")
        print("-" * 50)
        
        # ✅ Create customers with unique username+email combinations
        print("✅ Creating customers with unique data...")
        customer1 = Customer.objects.create(
            username="john_doe",
            email="john@example.com",
            phone="555-0101"
        )
        customer2 = Customer.objects.create(
            username="jane_smith",
            email="jane@example.com", 
            phone="555-0102"
        )
        print(f"   Created: {customer1}")
        print(f"   Created: {customer2}")
        
        # ❌ Try duplicate username+email combination (should fail)
        print("\n❌ Trying duplicate username+email combination...")
        try:
            duplicate_customer = Customer(
                username="john_doe",  # Same username as customer1
                email="john@example.com",  # Same email as customer1
                phone="555-9999"  # Different phone
            )
            duplicate_customer.save()
            self.fail("Should have failed due to unique_together constraint")
        except (ValidationError, IntegrityError) as e:
            print(f"   ✅ CORRECTLY BLOCKED: {type(e).__name__}")
            print("   Constraint working: Username + Email must be unique together")
        
        # ❌ Try duplicate phone number (should fail)
        print("\n❌ Trying duplicate phone number...")
        try:
            duplicate_phone_customer = Customer(
                username="different_user",
                email="different@example.com",
                phone="555-0101"  # Same phone as customer1
            )
            duplicate_phone_customer.save()
            self.fail("Should have failed due to unique phone constraint")
        except (ValidationError, IntegrityError) as e:
            print(f"   ✅ CORRECTLY BLOCKED: {type(e).__name__}")
            print("   Constraint working: Phone numbers must be unique")
        
        # ✅ Create customer with same username but different email (should work)
        print("\n✅ Creating customer with same username but different email...")
        customer3 = Customer.objects.create(
            username="john_doe",  # Same username as customer1
            email="john.doe.different@example.com",  # Different email
            phone="555-0103"
        )
        print(f"   ✅ SUCCESS: {customer3}")
        print("   Constraint working: Same username OK if different email")
        
        # ================================================================
        # PHASE 5: ORDER MANAGEMENT (unique_together constraints)
        # ================================================================
        print("\n\n🛒 PHASE 5: Order Management (unique_together)")
        print("-" * 45)
        
        # ✅ Create orders with unique order_number+customer combinations
        print("✅ Creating orders with unique order_number+customer...")
        order1 = Order.objects.create(
            order_number="ORD-2025-001",
            customer=customer1,
            total_amount=29.99
        )
        order2 = Order.objects.create(
            order_number="ORD-2025-002",
            customer=customer2,
            total_amount=45.50
        )
        print(f"   Created: {order1}")
        print(f"   Created: {order2}")
        
        # ✅ Same order number for different customers (should work)
        print("\n✅ Creating same order number for different customer...")
        order3 = Order.objects.create(
            order_number="ORD-2025-001",  # Same order number as order1
            customer=customer2,  # Different customer
            total_amount=15.99
        )
        print(f"   ✅ SUCCESS: {order3}")
        print("   Constraint working: Same order number OK for different customers")
        
        # ❌ Try duplicate order_number+customer combination (should fail)
        print("\n❌ Trying duplicate order_number+customer combination...")
        try:
            duplicate_order = Order(
                order_number="ORD-2025-001",  # Same as order1
                customer=customer1,  # Same customer as order1
                total_amount=99.99
            )
            duplicate_order.save()
            self.fail("Should have failed due to unique_together constraint")
        except (ValidationError, IntegrityError) as e:
            print(f"   ✅ CORRECTLY BLOCKED: {type(e).__name__}")
            print("   Constraint working: Order number + Customer must be unique together")
        
        # ================================================================
        # PHASE 6: SUMMARY AND VERIFICATION
        # ================================================================
        print("\n\n📊 PHASE 6: Final Summary")
        print("-" * 30)
        
        # Count final objects
        authors_count = Author.objects.count()
        books_count = Book.objects.count()
        locations_count = Location.objects.count()
        stock_count = Stock.objects.count()
        customers_count = Customer.objects.count()
        orders_count = Order.objects.count()
        
        print(f"📈 Final Object Counts:")
        print(f"   Authors: {authors_count} (1 inactive, 2 active)")
        print(f"   Books: {books_count} (all with unique ISBNs and title+author combinations)")
        print(f"   Locations: {locations_count} (all with unique codes)")
        print(f"   Stock Records: {stock_count} (1 inactive, 2 active)")
        print(f"   Customers: {customers_count} (all with unique username+email and phone)")
        print(f"   Orders: {orders_count} (all with unique order_number+customer)")
        
        print(f"\n🎯 Constraint Types Demonstrated:")
        print(f"   ✅ Conditional Constraints: Author emails, Stock records")
        print(f"   ✅ Non-conditional Constraints: Book ISBNs, Location codes")
        print(f"   ✅ unique_together Constraints: Book title+author, Customer data, Orders")
        print(f"   ✅ Multi-Database Routing: Books on 'default', Inventory+Customers on 'second_database'")
        
        print(f"\n🏆 ALL CONSTRAINTS WORKING PERFECTLY!")
        print("="*60)
        
        # Verify our expectations
        self.assertEqual(authors_count, 3)
        self.assertEqual(books_count, 4)
        self.assertEqual(locations_count, 2)
        self.assertEqual(stock_count, 3)
        self.assertEqual(customers_count, 3)
        self.assertEqual(orders_count, 3)


if __name__ == '__main__':
    # Allow running this test directly
    import unittest
    unittest.main()
