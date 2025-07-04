from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app.persistence.repository import SQLAlchemyRepository
from app import bcrypt

class HBnBFacade:
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(User)
        self.amenity_repo = SQLAlchemyRepository(Amenity)
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)

    def create_user(self, user_data):
        password = user_data.pop('password', None)
        if not password:
            raise ValueError("Password is required")

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_data['password_hash'] = hashed_password

        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, data):
        user = self.user_repo.get(user_id)
        if not user:
            return None

        for field in ('first_name', 'last_name', 'email'):
            if field in data:
                setattr(user, field, data[field])

        if 'password' in data:
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            user.password_hash = hashed_password

        self.user_repo.add(user)
        return user

    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None

        if 'name' in amenity_data:
            if len(amenity_data['name']) > 50:
                raise ValueError("Name must be 50 characters or fewer.")
            amenity.name = amenity_data['name']

        self.amenity_repo.add(amenity)
        return amenity

    def create_place(self, place_data):
        try:
            owner = self.user_repo.get(place_data['owner_id'])
            if not owner:
                raise ValueError("Owner not found")

            amenities = []
            for amenity_id in place_data.get('amenities', []):
                amenity = self.amenity_repo.get(amenity_id)
                if not amenity:
                    raise ValueError(f"Amenity ID {amenity_id} not found")
                amenities.append(amenity)

            place = Place(
                title=place_data['title'],
                description=place_data.get('description', ''),
                price=place_data['price'],
                latitude=place_data['latitude'],
                longitude=place_data['longitude'],
                owner=owner
            )
            for am in amenities:
                place.add_amenity(am)

            self.place_repo.add(place)
            return place
        except Exception as e:
            raise ValueError(str(e))

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, data):
        place = self.place_repo.get(place_id)
        if not place:
            return None

        for field in ['title', 'description', 'price', 'latitude', 'longitude']:
            if field in data:
                setattr(place, field, data[field])

        if 'amenities' in data:
            place.amenities = []
            for amenity_id in data['amenities']:
                amenity = self.amenity_repo.get(amenity_id)
                if not amenity:
                    raise ValueError(f"Amenity ID {amenity_id} not found")
                place.add_amenity(amenity)

        self.place_repo.add(place)
        return place

    def create_review(self, review_data):
        user = self.user_repo.get(review_data['user_id'])
        place = self.place_repo.get(review_data['place_id'])
        if not user or not place:
            raise ValueError("User or Place not found")

        rating = int(review_data['rating'])
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        review = Review(
            text=review_data['text'],
            rating=rating,
            place=place,
            user=user
        )
        self.review_repo.add(review)
        place.add_review(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")
        return place.reviews

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if not review:
            return None

        if 'text' in review_data:
            review.text = review_data['text']
        if 'rating' in review_data:
            rating = int(review_data['rating'])
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            review.rating = rating

        self.review_repo.add(review)
        return review

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if not review:
            return False

        review.place.reviews = [r for r in review.place.reviews if r.id != review_id]
        self.review_repo.delete(review_id)
        return True
