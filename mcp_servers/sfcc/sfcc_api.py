"""SFCC (Salesforce Commerce Cloud) notification API client."""

import requests
from typing import Optional


class SFCCAPI:
    """Client for SFCC SSE Hub notification API."""

    BASE_URL = "https://sfcc-sse-hub-agentforce-a10f0025fedb.herokuapp.com"

    def __init__(self, default_user_id: str = "cust:00000001"):
        self.default_user_id = default_user_id

    def _notify(self, user_id: str, notification_type: str, payload: dict) -> dict:
        """Send a notification to the SFCC SSE Hub."""
        response = requests.post(
            f"{self.BASE_URL}/notify",
            json={
                "userId": user_id,
                "type": notification_type,
                "payload": payload,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return {"success": True, "status_code": response.status_code}

    def show_banner(
        self, text: str, url: str, user_id: Optional[str] = None
    ) -> dict:
        """Show a banner with text and navigate to URL."""
        return self._notify(
            user_id or self.default_user_id,
            "SHOW_BANNER",
            {"text": text, "url": url},
        )

    def show_plp(
        self, text: str, category_path: str, user_id: Optional[str] = None
    ) -> dict:
        """
        Show Product Listing Page (PLP).

        Args:
            text: Banner text to display
            category_path: Category URL path (e.g., '/s/nto/default/shoes-men-hiking')
            user_id: Customer ID (defaults to configured user)
        """
        return self.show_banner(text, category_path, user_id)

    def show_pdp(
        self, text: str, product_url: str, user_id: Optional[str] = None
    ) -> dict:
        """
        Show Product Detail Page (PDP).

        Args:
            text: Banner text to display
            product_url: Product URL path (e.g., 's/nto/default/product-name.html')
            user_id: Customer ID (defaults to configured user)
        """
        return self.show_banner(text, product_url, user_id)

    def add_to_basket(
        self, sku: str, quantity: int = 1, user_id: Optional[str] = None
    ) -> dict:
        """
        Add item to shopping basket.

        Args:
            sku: Product SKU
            quantity: Quantity to add
            user_id: Customer ID (defaults to configured user)
        """
        return self._notify(
            user_id or self.default_user_id,
            "ADD_TO_BASKET",
            {"quantity": str(quantity), "sku": sku},
        )

    def start_checkout(self, user_id: Optional[str] = None) -> dict:
        """
        Navigate to checkout page.

        Args:
            user_id: Customer ID (defaults to configured user)
        """
        return self.show_banner(
            "Checking out...",
            "checkout?stage=payment#payment",
            user_id,
        )

    def submit_payment(
        self,
        first_name: str,
        last_name: str,
        address1: str,
        city: str,
        postal_code: str,
        country: str,
        state_code: str,
        phone: str,
        card_type: str,
        card_number: str,
        card_owner: str,
        exp_month: str,
        exp_year: str,
        security_code: str,
        address2: str = "",
        save_card: bool = True,
        user_id: Optional[str] = None,
    ) -> dict:
        """
        Submit payment and place order.

        Args:
            first_name: Customer first name
            last_name: Customer last name
            address1: Primary address line
            city: City
            postal_code: Postal/ZIP code
            country: Country code (e.g., 'US')
            state_code: State code (e.g., 'AK')
            phone: Phone number
            card_type: Card type (e.g., 'Visa', 'Mastercard')
            card_number: Card number
            card_owner: Name on card
            exp_month: Expiration month
            exp_year: Expiration year
            security_code: CVV/security code
            address2: Secondary address line (optional)
            save_card: Whether to save card for future use
            user_id: Customer ID (defaults to configured user)
        """
        return self._notify(
            user_id or self.default_user_id,
            "SUBMIT_PAYMENT",
            {
                "firstName": first_name,
                "lastName": last_name,
                "address1": address1,
                "address2": address2,
                "city": city,
                "postalCode": postal_code,
                "country": country,
                "stateCode": state_code,
                "phone": phone,
                "cardType": card_type,
                "cardNumber": card_number,
                "cardOwner": card_owner,
                "expMonth": exp_month,
                "expYear": exp_year,
                "securityCode": security_code,
                "saveCard": save_card,
            },
        )

    def set_discount(
        self, discount_percent: int, user_id: Optional[str] = None
    ) -> dict:
        """
        Set a negotiated discount for the session.

        Args:
            discount_percent: Discount percentage (e.g., 10 for 10%)
            user_id: Customer ID (defaults to configured user)
        """
        return self._notify(
            user_id or self.default_user_id,
            "SET_SESSION",
            {"key": "negotiated", "value": str(discount_percent)},
        )

    def show_order_history(self, user_id: Optional[str] = None) -> dict:
        """
        Navigate to order history page.

        Args:
            user_id: Customer ID (defaults to configured user)
        """
        return self.show_banner(
            "Here are your orders...",
            "orders",
            user_id,
        )
