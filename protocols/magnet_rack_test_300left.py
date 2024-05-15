"""
Testing the magnetic rack and the depth of pipette tips in the wells on the rack
"""
import math
#from opentrons import protocol_api
from opentrons import types


metadata = {
    'protocolName': 'Testing the magnet rack - P300 on left',
    'author': 'Takács Bertalan <bertalan.takacs@deltabio.eu>',
    'source': 'DeltaBio',
    'apiLevel': '2.14'
}


def run(protocol_context):

    sample_number = 8


    #defining modules, tipracks and pipettes
    mag_deck = protocol_context.load_module("magnetic module gen2", '1')
    
    mag_plate = mag_deck.load_labware(
        'biorad_96_wellplate_200ul_pcr')
    
    output_plate = protocol_context.load_labware(
        'biorad_96_wellplate_200ul_pcr', '2', 'output plate')
    
    reagent_container = protocol_context.load_labware(
        'usascientific_12_reservoir_22ml', '4')

    total_tips_200 = sample_number * 8
    total_tips_20 = sample_number
    tiprack_num_200 = math.ceil(total_tips_200 / 96)
    tiprack_num_20 = math.ceil(total_tips_20 / 96)

    tipracks_200 = [
            protocol_context.load_labware(
                load_name="opentrons_96_tiprack_300ul", location=slot)
            for slot in ['3', '5', '6', '7', '8', '9'][:tiprack_num_200]
        ]
    tipracks_20 = [
        protocol_context.load_labware(
            load_name="opentrons_96_tiprack_20ul", location=slot)
        for slot in ['10','11'][:tiprack_num_20]
    ]


    p20_pipette = protocol_context.load_instrument(
        instrument_name="p20_multi_gen2",
        mount="right",
        tip_racks=tipracks_20)
    
    p300_pipette = protocol_context.load_instrument(
        instrument_name="p300_multi_gen2",
        mount="left",
        tip_racks=tipracks_200)

    #p300 goes too deep into the reservoir
    #p300_pipette.well_bottom_clearance.aspirate = 2

    #Aspiration is too fast, try to slow down
    p300_pipette.flow_rate.aspirate = 10
    p300_pipette.flow_rate.dispense = 20

    p20_pipette.flow_rate.aspirate = 10
    p20_pipette.flow_rate.dispense = 20

    
    col_num = math.ceil(sample_number / 8)
    samples = [col for col in mag_plate.rows()[0][:col_num]]

    # Define reagents and liquid waste
    water = reagent_container.wells()[0]
    liquid_waste = reagent_container.wells()[-1]

    mix_vol = 50

    #test aspiration and mix with magnet rack engaged and disengaged
    #For P300
    for target in samples:
        p300_pipette.pick_up_tip()
        p300_pipette.transfer(mix_vol, water, target.bottom(z = 3), new_tip='never', blow_out = True)
        p300_pipette.mix(10, mix_vol, target.bottom(z = 3))
        p300_pipette.blow_out(target)
        p300_pipette.drop_tip()

    mag_deck.engage()

    for target in samples:
        p300_pipette.pick_up_tip()
        p300_pipette.mix(10, mix_vol, target.bottom(z = 3))
        p300_pipette.blow_out()
        p300_pipette.drop_tip()

    mag_deck.disengage()

    #For P20
    for target in samples:
        p20_pipette.pick_up_tip()
        p20_pipette.mix(10, 10, target.bottom(z = 2))
        p20_pipette.blow_out()
        p20_pipette.drop_tip()

    mag_deck.engage()

    for target in samples:
        p20_pipette.pick_up_tip()
        p20_pipette.mix(10, 10, target.bottom(z = 2))
        p20_pipette.blow_out()
        p20_pipette.drop_tip()

    mag_deck.disengage()

