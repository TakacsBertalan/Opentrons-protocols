"""
Testing the tip pickup
"""
import math
#from opentrons import protocol_api
from opentrons import types


metadata = {
    'protocolName': 'Pickup tip test',
    'author': 'Takács Bertalan <bertalan.takacs@deltabio.eu>',
    'source': 'DeltaBio',
    'apiLevel': '2.14'
}


def run(protocol_context):

    mag_deck = protocol_context.load_module("magnetic module gen2", '1')
    mag_plate = mag_deck.load_labware(
        'biorad_96_wellplate_200ul_pcr')
    tiprack_num_200 = 1
    tiprack_num_20 = 1

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

    #test aspiration and mix with magnet rack engaged and disengaged
    #For P300
    mag_deck.engage()

    for _ in range(6):
        p300_pipette.pick_up_tip()
        p300_pipette.return_tip()

    #For P20
    for _ in range(6):
        p20_pipette.pick_up_tip()
        p20_pipette.return_tip()

    mag_deck.disengage()
