import os
import random
import time

from collections.abc import Iterator
from dotenv import load_dotenv

import dungeons_and_trolls_client as dnt
from dungeons_and_trolls_client.models.dungeonsandtrolls_attributes import DungeonsandtrollsAttributes
from dungeons_and_trolls_client.models.dungeonsandtrolls_character import DungeonsandtrollsCharacter
from dungeons_and_trolls_client.models.dungeonsandtrolls_coordinates import DungeonsandtrollsCoordinates
from dungeons_and_trolls_client.models.dungeonsandtrolls_game_state import DungeonsandtrollsGameState
from dungeons_and_trolls_client.models.dungeonsandtrolls_identifiers import DungeonsandtrollsIdentifiers
from dungeons_and_trolls_client.models.dungeonsandtrolls_item import DungeonsandtrollsItem
from dungeons_and_trolls_client.models.dungeonsandtrolls_item_type import DungeonsandtrollsItemType
from dungeons_and_trolls_client.models.dungeonsandtrolls_level import DungeonsandtrollsLevel
from dungeons_and_trolls_client.models.dungeonsandtrolls_map_objects import DungeonsandtrollsMapObjects
from dungeons_and_trolls_client.models.dungeonsandtrolls_message import DungeonsandtrollsMessage
from dungeons_and_trolls_client.models.dungeonsandtrolls_monster import DungeonsandtrollsMonster
from dungeons_and_trolls_client.models.dungeonsandtrolls_skill import DungeonsandtrollsSkill
from dungeons_and_trolls_client.models.dungeonsandtrolls_skill_use import DungeonsandtrollsSkillUse
from dungeons_and_trolls_client.models.skill_target import SkillTarget
from dungeons_and_trolls_client.rest import ApiException

load_dotenv()

configuration = dnt.Configuration(
    host = os.getenv("HOST"),
    api_key = {'ApiKeyAuth': os.getenv("API_KEY")}
)

# Computes dot product for the given wepon and character attritbutes.
def compute_damage(skill_damage_amount: DungeonsandtrollsAttributes, character_attributes: DungeonsandtrollsAttributes) -> float:
    return sum([weapon_val * getattr(character_attributes, attr_name, 0) 
                for attr_name, weapon_val in skill_damage_amount.to_dict().items()
                if weapon_val])

# Chooses free weapon.
def choose_best_weapon(weapons: Iterator[DungeonsandtrollsItem], character_attributes: DungeonsandtrollsAttributes, budget: int) -> DungeonsandtrollsItem:
    currentWeapon = None
    currentDamage = 0
    for weapon in weapons:
        weapon : DungeonsandtrollsItem
        if weapon.price == 0:
            currentWeapon = weapon
            break
    if currentWeapon is not None:
        print("Buying", currentWeapon.name)
    return currentWeapon

def assign_skill_points(character: DungeonsandtrollsCharacter, api_instance: dnt.DungeonsAndTrollsApi) -> bool:
    if character.skill_points == 0:
        return False
    attr: DungeonsandtrollsAttributes = DungeonsandtrollsAttributes(stamina=character.skill_points)
    api_instance.dungeons_and_trolls_assign_skill_points(attr)
    print("Assigning " + str(character.skill_points) + " skill points to stamina")
    return True

# Optimization function to select the best gear for the player based on budget.
def select_gear(items: list[DungeonsandtrollsItem], character: DungeonsandtrollsCharacter) -> DungeonsandtrollsIdentifiers:
    gear = DungeonsandtrollsIdentifiers()
    gear.ids = []
    equiped = set([equip.id for equip in character.equip])
    weapons = filter(lambda x: x.slot == DungeonsandtrollsItemType.MAINHAND, items)
    armor = filter(lambda x: x.slot in {DungeonsandtrollsItemType.BODY,
                                        DungeonsandtrollsItemType.HEAD,
                                        DungeonsandtrollsItemType.LEGS,
                                        DungeonsandtrollsItemType.NECK}, items)
    # TODO select armor
    weapon = choose_best_weapon(weapons, character.attributes, character.money)
    gear.ids = [weapon.id] if weapon and str(weapon.id) not in equiped else []
    return gear

# Buy the provided gear, if there is any.
def maybe_buy_gear(gear: DungeonsandtrollsIdentifiers, api_instance: dnt.DungeonsAndTrollsApi):
    if len(gear.ids) > 0:
        api_instance.dungeons_and_trolls_buy(gear)

# Check the skill cost against the character attributes.
def can_character_use_skill(skill_cost: DungeonsandtrollsAttributes, character_attributes: DungeonsandtrollsAttributes) -> bool:
    for cost_attr_key, cost_attr_val in skill_cost.to_dict().items():
        if cost_attr_val and getattr(character_attributes, cost_attr_key, 0) < cost_attr_val:
            print("missing attribute " + cost_attr_key + " required: " + str(cost_attr_val) + ", have: " + str(getattr(character_attributes, cost_attr_key, 0)))
            return False
    return True

# Select skill that deals any damage.
def select_skill(items: Iterator[DungeonsandtrollsItem], character_attrs: DungeonsandtrollsAttributes) -> DungeonsandtrollsSkill:
    for item in items:
        skill : DungeonsandtrollsSkill = None
        for skill in item.skills:
            can_use_skill = can_character_use_skill(skill.cost, character_attrs)
            skill.target : SkillTarget
            if skill.target != SkillTarget.CHARACTER:
                can_use_skill = False
            if can_use_skill:
                return skill
    return None

# Search for a tile with stairs on it.
def find_stairs_to_next_level(game: DungeonsandtrollsGameState) -> DungeonsandtrollsCoordinates:
    level : DungeonsandtrollsLevel = (game.map.levels[0])
    for object in level.objects:
        object : DungeonsandtrollsMapObjects
        if (object.is_stairs):
            return object.position
        
# Find any monster on the current level.
def find_monster(game: DungeonsandtrollsGameState) -> (DungeonsandtrollsMonster, DungeonsandtrollsCoordinates):
    level : DungeonsandtrollsLevel = (game.map.levels[0])
    for obj in level.objects:
        if not obj.monsters:
            continue
        for monster in obj.monsters:
            monster: DungeonsandtrollsMonster
            return monster, obj.position
    return None, None

# Update the monster information, e.g. position if the monster moved recently.
def update_monster(monster_id: str, game: DungeonsandtrollsGameState) -> (DungeonsandtrollsMonster, DungeonsandtrollsCoordinates):
    level : DungeonsandtrollsLevel = game.map.levels[0]
    for obj in level.objects:
        obj: DungeonsandtrollsMapObjects
        for monster in obj.monsters:
            monster: DungeonsandtrollsMonster
            if monster.id == monster_id:
                return monster, obj.position
    return None, None

# Compare whether two game objects are on the same tile.
def on_the_same_position(a: DungeonsandtrollsCoordinates, b: DungeonsandtrollsCoordinates) -> bool:
    return a.position_x == b.position_x and a.position_y == b.position_y

def main():
    # Enter a context with an instance of the API client
    with dnt.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = dnt.DungeonsAndTrollsApi(api_client)

        monster_pos : DungeonsandtrollsCoordinates = None
        monster : DungeonsandtrollsMonster = None

        while True:
            try:
                print("----------")
                game = api_instance.dungeons_and_trolls_game()
                print("current level", game.current_level)

                if assign_skill_points(game.character, api_instance):
                    continue

                # buy and equip items
                maybe_buy_gear(select_gear(game.shop_items, game.character), api_instance)
                    
                if monster_pos is None:
                    # locate any monster on current level
                    print("locating monster")
                    monster, monster_pos = find_monster(game)
                    
                    if monster is None:
                        print("no monster on level, moving to stairs")
                        api_instance.dungeons_and_trolls_move(find_stairs_to_next_level(game))
                        continue
                else:
                    # update information for existing monster
                    monster, monster_pos = update_monster(monster.id, game)
                    if not monster:
                        continue
                
                character_pos : DungeonsandtrollsCoordinates = game.current_position
                if on_the_same_position(monster_pos, character_pos):
                    # select skill
                    print("selecting a skill to fight with")
                    skill = select_skill(
                        # filter only MAINHAND items
                        filter(lambda x: x.slot == DungeonsandtrollsItemType.MAINHAND, game.character.equip),
                        game.character.attributes)
                    if not skill:
                        print("I can't use skill!")
                        continue
                    skill_damage = compute_damage(skill.damage_amount, game.character.attributes)
                    # fight the monster
                    print("fighting with " + skill.name + "! Damage dealt: " + str(skill_damage) + " monster life: " + str(monster.life_percentage))
                    try:
                        api_instance.dungeons_and_trolls_skill(DungeonsandtrollsSkillUse(skillId=skill.id, targetId=monster.id))
                    except ApiException as e:
                        monster, monster_pos = None, None
                        continue
                else:
                    # move to the monster
                    print("moving to monster on pos: " + str(monster_pos) + ", my pos: " + str(character_pos))
                    api_instance.dungeons_and_trolls_move(monster_pos)

            except ApiException as e:
                print("Exception when calling DungeonsAndTrollsApi: %s\n" % e)

if __name__ == "__main__":
    main()
