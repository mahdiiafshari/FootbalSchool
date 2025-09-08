from rest_framework import serializers
from .models import Coach
from account.models import Profile, User

class CoachSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    national_id = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True)
    image_profile = serializers.ImageField(write_only=True, required=False)
    emergency_phone = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Coach
        fields = [
            "id", "user", "manager", "school",
            "cooperation_start_date",
            "full_name", "national_id", "phone_number",
            "date_of_birth", "image_profile", "emergency_phone", "password"
        ]
        read_only_fields = ["user", "manager", "school"]

    def create(self, validated_data):
        request = self.context["request"]
        manager = getattr(request.user, "manager", None)
        if not manager or not manager.school:
            raise serializers.ValidationError("Manager must have a school before adding coaches.")

        # Pop extra fields
        full_name = validated_data.pop("full_name")
        national_id = validated_data.pop("national_id")
        phone_number = validated_data.pop("phone_number")
        date_of_birth = validated_data.pop("date_of_birth")
        image_profile = validated_data.pop("image_profile", None)
        emergency_phone = validated_data.pop("emergency_phone", None)
        password = validated_data.pop("password")

        # Create User
        user = User.objects.create_user(
            phone_number=phone_number,
            password=password,
            role="coach"
        )

        # Create Profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.full_name = full_name
        profile.national_code = national_id
        profile.phone = phone_number
        profile.date_of_birth = date_of_birth
        profile.image_profile = image_profile
        profile.emergency_phone = emergency_phone
        profile.save()

        coach = Coach.objects.create(
            user=user,
            manager=manager,
            school=manager.school,
            cooperation_start_date=validated_data.get("cooperation_start_date")
        )
        return coach

    def update(self, instance, validated_data):
        user = instance.user
        profile, _ = Profile.objects.get_or_create(user=user)

        # Update related fields
        if "phone_number" in validated_data:
            user.phone_number = validated_data.pop("phone_number")
            user.save()

        profile.full_name = validated_data.pop("full_name", profile.full_name)
        profile.national_code = validated_data.pop("national_id", profile.national_code)
        profile.phone = user.phone_number
        profile.date_of_birth = validated_data.pop("date_of_birth", profile.date_of_birth)
        profile.image_profile = validated_data.pop("image_profile", profile.image_profile)
        profile.emergency_phone = validated_data.pop("emergency_phone", profile.emergency_phone)
        profile.save()

        return super().update(instance, validated_data)
