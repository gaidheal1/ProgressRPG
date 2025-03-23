from rest_framework import serializers


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ['id', 'name', 'xp', 'xp_next_level', 'xp_modifier', 'level', 'total_quests']

    def __init__(self, *args, **kwargs):
        from .models import Character
        self.Meta.model = Character
        super().__init__(*args, **kwargs)