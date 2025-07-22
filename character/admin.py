from django.contrib import admin
from .models import (
    Character,
    PlayerCharacterLink,
    CharacterRelationship,
    CharacterRole,
    CharacterProgression,
)

# Register your models here.

from django.contrib import messages


class LinkInline(admin.TabularInline):
    model = PlayerCharacterLink


@admin.action(description="Mark selected characters as NPCs and unlink from profiles")
def mark_as_npc(modeladmin, request, queryset):
    for character in queryset:
        # Unlink any active PlayerCharacterLink
        active_links = character.profile_link.filter(is_active=True)
        for link in active_links:
            link.unlink()

        # Mark character as NPC
        character.is_npc = True
        character.save(update_fields=["is_npc"])

    messages.success(
        request, f"{queryset.count()} character(s) marked as NPC and unlinked."
    )


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    # def current_player(self, obj):
    #     link = PlayerCharacterLink.objects.filter(character=obj, is_active=True).first()
    #     return link.profile.name if link else 'No player linked'

    # current_player.short_description = 'Current Player'
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "is_npc")}),
        ("Life & Story", {"fields": ("backstory", "parents", "sex")}),
        (
            "Pregnancy Details",
            {
                "fields": (
                    ("is_pregnant", "pregnancy_start_date", "pregnancy_due_date"),
                )
            },
        ),
        ("Dates", {"fields": (("birth_date", "death_date"), "cause_of_death")}),
        ("Stats", {"fields": ("coins", "reputation", "total_quests")}),
    )

    list_display = [
        "first_name",
        "last_name",
        "backstory",
        "get_profile",
        "is_npc",
        "birth_date",
    ]
    list_filter = [
        "is_npc",
    ]
    # list_editable = ['birth_date']
    search_fields = [
        "first_name",
        "last_name",
    ]
    readonly_fields = [
        "get_profile",
    ]
    inlines = [LinkInline]
    actions = [mark_as_npc]

    @admin.display(description="Profile")
    def get_profile(self, obj):
        try:
            return PlayerCharacterLink.get_profile(obj)
        except ValueError:
            return "-"

    @admin.display(boolean=True, description="Has Profile")
    def has_profile(self, obj):
        return PlayerCharacterLink.objects.filter(
            character=obj, is_active=True
        ).exists()


# admin.site.register(Character, CharacterAdmin)


@admin.register(PlayerCharacterLink)
class PlayerCharacterLinkAdmin(admin.ModelAdmin):
    list_display = ["profile", "character", "is_active"]
    fields = ["profile", "character", "is_active"]  # ('date_linked', 'date_unlinked'),


class CharacterInline(admin.TabularInline):
    model = (
        CharacterRelationship.characters.through
    )  # Access the ManyToMany through model
    extra = 1


@admin.register(CharacterRelationship)
class CharacterRelationshipAdmin(admin.ModelAdmin):
    list_display = [
        "relationship_type",
        "get_linked_characters",
        "last_updated",
    ]
    fields = [
        "relationship_type",
        "strength",
        "history",
        "biological",
        ("created_at", "last_updated"),
    ]
    inlines = [CharacterInline]
    readonly_fields = ["created_at", "last_updated"]
    filter_horizontal = [
        "characters",
    ]

    @admin.display(description="Characters")
    def get_linked_characters(self, obj):
        return ", ".join([str(char) for char in obj.get_members()])


@admin.register(CharacterRole)
class CharacterRoleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
    ]


@admin.register(CharacterProgression)
class CharacterProgressionAdmin(admin.ModelAdmin):
    list_display = [
        "character",
        "role",
    ]
    fields = [
        "character",
        "role",
        "experience",
        "date_started",
        "base_progression_rate",
        "player_acceleration_factor",
    ]
