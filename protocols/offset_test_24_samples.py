import math
#from opentrons import protocol_api
from opentrons import types
def modify_tip_position(target, xoffset, zoffset, toporbottom, first_line):
    if toporbottom == "top":
        center_location = target.top(z = zoffset)
    else:
        center_location = target.bottom(z = zoffset)
    #pozitív értékek jobbra, negatívak balra mozgatják a hegyet
    if first_line == "bal":
        xoffset = -1 * xoffset
    if target.well_name[0] in ["A", "C", "E", "G", "I", "K", "M"]:
        # Páratlan számú sorokban jobbra 1 mm-el
        altered_position = center_location.move(types.Point(x=xoffset, y=0, z=0))
    else:
        # Páros számú sorokban balra 1 mm-el
        altered_position = center_location.move(types.Point(x=-1*xoffset, y=0, z=0))
    return altered_position



metadata = {
    'protocolName': 'Test - z and x offsets - 24 samples',
    'author': 'Takács Bertalan <bertalan.takacs@deltabio.eu>',
    'source': 'DeltaBio',
    'apiLevel': '2.14'
}

def run(protocol_context):

    sample_number = 24
    mag_deck = protocol_context.load_module(mag_mod, '1')
    mag_plate = mag_deck.load_labware(
        'biorad_96_wellplate_200ul_pcr')

    total_tips_ketszaz = sample_number * 8
    total_tips_10 = sample_number
    tiprack_num_ketszaz = math.ceil(total_tips_ketszaz / 96)
    tiprack_num_10 = math.ceil(total_tips_10 / 96)

    tipracks_200 = [
        protocol_context.load_labware(
            load_name="opentrons_96_tiprack_300ul", location=slot)
        for slot in ['3', '5', '6', '7', '8', '9'][:tiprack_num_ketszaz]
    ]
    tipracks_20 = [
        protocol_context.load_labware(
            load_name="opentrons_96_tiprack_20ul", location=slot)
        for slot in ['10','11'][:tiprack_num_10]
    ]

    p20_pipette = protocol_context.load_instrument(
        instrument_name="p20_multi_gen2",
        mount="right",
        tip_racks=tipracks_20)
    p300_pipette = protocol_context.load_instrument(
        instrument_name="p300_multi_gen2",
        mount="left",
        tip_racks=tipracks_200)

    mode = pipette_type.split('_')[1]
    #p300_pipette.well_bottom_clearance.dispense = 2

    reagent_container = protocol_context.load_labware(
        'nest_12_reservoir_15ml', '4')
    liquid_waste = reagent_container.wells()[-1]
    col_num = math.ceil(sample_number / 8)
    samples = [col for col in mag_plate.rows()[0][:col_num]]
    output = [col for col in output_plate.rows()[0][:col_num]]

    # Define reagents and liquid waste
    water = reagent_container.wells()[0]

    mag_deck.engage(height_from_base=9)
    
    for target in samples:
        p300_pipette.pick_up_tip()
        adjusted_location = modify_tip_position(target, 2, 2, "bottom", "bal")
        p300_pipette.transfer(mix_vol, water, adjusted_location, new_tip='never')
        p300_pipette.return_tip()

    for target in samples:
        p300_pipette.pick_up_tip()
        adjusted_location = modify_tip_position(target, 2, 2, "bottom", "jobb")
        p300_pipette.transfer(mix_vol, water, adjusted_location, new_tip='never')
        p300_pipette.return_tip()

    #For P20
    for target in samples:
        p20_pipette.pick_up_tip()
        adjusted_location = modify_tip_position(target, 2, 1, "bottom", "jobb")
        300_pipette.transfer(mix_vol, water, adjusted_location, new_tip='never')
        p300_pipette.return_tip()

mag_deck.disengage()
