from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('reviews', description='Review operations')

# Client sends: comment, rating, place_id  (user_id comes from JWT)
review_model = api.model('Review', {
    'comment': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

# What we return
review_output = api.inherit('ReviewOut', review_model, {
    'id': fields.String(description='Review ID'),
    'user_id': fields.String(description='ID of the user who wrote the review')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.marshal_with(review_output, code=201)
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()                  # STRING user id
        claims = get_jwt()
        is_admin = bool(claims.get('is_admin', False))
        payload = dict(api.payload or {})

        # Accept 'text' from older clients but normalize to 'comment'
        if 'text' in payload and 'comment' not in payload:
            payload['comment'] = payload.pop('text')

        # Non-admins can only post as themselves; admins may optionally specify user_id
        if not is_admin:
            payload['user_id'] = user_id
        else:
            payload['user_id'] = payload.get('user_id') or user_id

        try:
            review = facade.create_review(payload)
            return review, 201
        except ValueError as ve:
            return {'error': str(ve)}, 400

    @api.marshal_list_with(review_output)
    def get(self):
        return facade.get_all_reviews()


@api.route('/<string:review_id>')
class ReviewResource(Resource):
    @api.marshal_with(review_output)
    def get(self, review_id):
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")
        return review

    @api.expect(review_model)
    @jwt_required()
    def put(self, review_id):
        user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = bool(claims.get('is_admin', False))
        review = facade.get_review(review_id)

        if not review:
            api.abort(404, "Review not found")

        if not is_admin and review.user_id != user_id:
            return {'error': 'Unauthorized action'}, 403

        payload = dict(api.payload or {})
        if 'text' in payload and 'comment' not in payload:
            payload['comment'] = payload.pop('text')

        try:
            updated = facade.update_review(review_id, payload)
            return {'message': 'Review updated successfully'}, 200
        except ValueError as ve:
            return {'error': str(ve)}, 400

    @jwt_required()
    def delete(self, review_id):
        user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = bool(claims.get('is_admin', False))
        review = facade.get_review(review_id)

        if not review:
            api.abort(404, "Review not found")

        if not is_admin and review.user_id != user_id:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200


@api.route('/places/<string:place_id>/reviews')
class PlaceReviewList(Resource):
    @api.marshal_list_with(review_output)
    def get(self, place_id):
        try:
            return facade.get_reviews_by_place(place_id)
        except ValueError as ve:
            return {'error': str(ve)}, 404
