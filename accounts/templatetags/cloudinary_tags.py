"""
Template tags for Cloudinary image transformations.
"""
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def cloudinary_url(image_field, transformation='c_fill,g_face,h_400,w_400'):
    """
    Returns a Cloudinary URL with transformations applied.

    Usage: {{ user.profile_picture|cloudinary_url }}
    Or with custom transformation: {{ user.profile_picture|cloudinary_url:"c_fill,h_200,w_200" }}

    Args:
        image_field: ImageField instance
        transformation: Cloudinary transformation string

    Returns:
        Full Cloudinary URL with transformations, or regular URL if not using Cloudinary
    """
    if not image_field:
        return ''

    url = image_field.url

    # Check if using Cloudinary (URL will contain cloudinary.com)
    if 'cloudinary.com' in url and transformation:
        # Insert transformation before the version number
        # Example: .../upload/v123/image.jpg -> .../upload/c_fill,w_400/v123/image.jpg
        parts = url.split('/upload/')
        if len(parts) == 2:
            return f"{parts[0]}/upload/{transformation}/{parts[1]}"

    return url
