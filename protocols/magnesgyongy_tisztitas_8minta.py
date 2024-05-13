"""
Saját protokollunk:

OPENTRONS OT-2 Mágnesgyöngyös tisztítás V1:

X = mintaszám (ideálisan 8-al osztható)

Műanyag: ketszazuL tip - x*8 (min. 1 rack), 10uL tip - x*1 (min. 1 rack), 96-os plate –2db, reagens resrevoir-1db

Vegyszer: mágnesgyöngy - x*36uL + 10% (min. X uL), 80%-os alkohol – x*400uL+10% (min. X uL), AG-MQ – x*22uL, (min. X uL)

#Az első sor a mágnesen jobb oldal
#Utána felváltva jobb-bal

Munkafolyamat:

1. Tisztítandó térfogat: 20uL.

1.5. Szuszpendálni 150 uL-el. 5-ször! BELEÍRNI!!

2. Hozzámért gyöngy: 36uL (1.8x).

3. Fel-le pipettázni 10 alkalommal 50uL-re állítva, hegyet kidob.

4. Inkubálni a plate-et  5 percig.

5. Mágnesállványt felemel.
Kevésbé magasra
6. 5 perc inkubálás.

7. Leszívni 55uL-et és kidobni (hegyet is). -innentől kezdve jó lenne, ha nem pont a lyuk közepére célozná a hegyet, hanem a pellettel ellentétes oldalra
7.a Mikor kiveszi, álljon meg


8. ketszaz uL 80%-os alkoholt rámérni, hegyet kidob.
8. Gyorsabban!
8. Túlszívta
8. Magasabbra a végét!

9. 30 mp-ig inkubálni.

10. Leszívni a ketszaz uL 80% alkoholt, hegyet kidob.

11. ketszaz uL 80%-os alkoholt rámérni, hegyet kidob.

12. 30 mp-ig inkubálni.

13. Leszívni a ketszaz uL 80% alkoholt, hegyet kidob.

14. 10uL-es hegy-el leszívni a maradékot, 10 uL hegyet kidob.

15. 3 perc inkubálás mágnesállvánnyal fent

Itt jó lenne, ha csak akkor menne tovább a protokoll, ha én már úgy látom, hogy lehet.

16. Mágnesállványt le.

17. 22uL AG-MilliQ rámérése. - itt a pellettel megegyező oldalra közelíthet

18. 10 alkalommal Fel-le pipettáz 20uL-et, hegyet kidob.

19. Inkubálás 2 percig.

20. Mágnesállványt felemel.

21. Inkubál 3 percig

22. Leszív 20uL-t -itt ismét a pellettel ellentétes oldalra

23. Áthelyez egy tiszta plate-be. - mehet középre

24. Hegyet kidob minden sor után.

25. Mágnesállvány le, plate a kukába.



Megjegyzés:

Gyakorláshoz javasolt OncoFREE kész könyvtárak, 1 sor (8 minta) előtte-utána futtatni TS-en, mérni Qubit-on.

"""
import math
#from opentrons import protocol_api
from opentrons import types
def modify_tip_position(target, offset, first_line):
    center_location = target.center()
    #pozitív értékek jobbra, negatívak balra mozgatják a hegyet
    if first_line == "bal":
        offset = -1 * offset
    if target.well_name[0] in ["A", "C", "E", "G", "I", "K", "M"]:
        # Páratlan számú sorokban jobbra 1 mm-el
        altered_position = center_location.move(types.Point(x=offset, y=0, z=0))
    else:
        # Páros számú sorokban balra 1 mm-el
        altered_position = center_location.move(types.Point(x=-1*offset, y=0, z=0))
    return altered_position

def get_values(*names):
    import json
    _all_values = json.loads(
        """{"mag_mod":"magnetic module gen2","pipette_type":"p300_single_gen2","pipette_mount":"left","sample_number":8,"sample_volume":20,"bead_ratio":1.8,"elution_buffer_volume":22,"incubation_time":1,"settling_time":1,"drying_time":5}""")
    return [_all_values[n] for n in names]


metadata = {
    'protocolName': 'DNA Purification - 8 samples',
    'author': 'Takács Bertalan <bertalan.takacs@deltabio.eu>',
    'source': 'Opentrons Protocol Library',
    'apiLevel': '2.14'
}


def run(protocol_context):

    [mag_mod, pipette_type, pipette_mount, sample_number, sample_volume,
     bead_ratio, elution_buffer_volume, incubation_time, settling_time,
     drying_time] = get_values(  # noqa: F821
        "mag_mod", "pipette_type", "pipette_mount", "sample_number",
        "sample_volume", "bead_ratio", "elution_buffer_volume",
        "incubation_time", "settling_time", "drying_time"
    )

    mag_deck = protocol_context.load_module(mag_mod, '1')
    mag_plate = mag_deck.load_labware(
        'biorad_96_wellplate_200ul_pcr')
    output_plate = protocol_context.load_labware(
        'biorad_96_wellplate_200ul_pcr', '2', 'output plate')

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

    #Ennyi miliméterrel mozgatjuk el a hegyet
    general_offset = 0.5

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
    beads = reagent_container.wells()[0]
    ethanol = reagent_container.wells()[1]
    elution_buffer = reagent_container.wells()[2]

    # Define bead and mix volume
    bead_volume = sample_volume * bead_ratio


    #Berci
    mix_vol = 50
    total_vol = bead_volume + sample_volume + 5

    # Mix beads and PCR samples
    #1. Tisztítandó térfogat: 20uL.

    #2. Hozzámért gyöngy: 36uL (1.8x).

    #3. Fel-le pipettázni 10 alkalommal 50uL-re állítva, hegyet kidob.
    p300_pipette.pick_up_tip()
    p300_pipette.mix(5,150,beads)
    
    for target in samples:
        #p300_pipette.pick_up_tip()
        p300_pipette.transfer(bead_volume, beads, target, new_tip='never')
        p300_pipette.mix(10, mix_vol, target)
        p300_pipette.blow_out()
        p300_pipette.drop_tip()

    #4. Inkubálni a plate-et  5 percig.
    protocol_context.delay(minutes=0.5)

    #5. Mágnesállványt felemel. (=engage)
    mag_deck.engage(height_from_base=9)
    #6. 5 perc inkubálás.
    protocol_context.delay(minutes=0.5)

    #A pipettázás sebességét adja meg
    p300_pipette.flow_rate.aspirate = 10
    p300_pipette.flow_rate.dispense = 50

    #7. Leszívni 55uL-et és kidobni (hegyet is). -innentől kezdve jó lenne, ha nem pont a lyuk közepére célozná a hegyet, hanem a pellettel ellentétes oldalra
    #Tehát első sor balra
    #Utána váltakozva
    p300_pipette.flow_rate.aspirate = 5

    for target in samples:
        #adjusted_location = modify_tip_position(target, general_offset, "bal")
        #Berci

        p300_pipette.transfer(55, target.bottom(z = 2).move(types.Point(x=-2)), liquid_waste, blow_out=True)

    p300_pipette.flow_rate.aspirate = 10
    #8. ketszaz uL 80%-os alkoholt rámérni, hegyet kidob.

    #9. 30 mp-ig inkubálni.

    #10. Leszívni a ketszaz uL 80% alkoholt, hegyet kidob.

    #11. ketszaz uL 80%-os alkoholt rámérni, hegyet kidob.

    #12. 30 mp-ig inkubálni.

    #13. Leszívni a ketszaz uL 80% alkoholt, hegyet kidob.
    p300_pipette.flow_rate.aspirate = 50
    for cycle in range(2):
        for target in samples:
            #adjusted_location = modify_tip_position(target, general_offset, "bal")
            # Berci
            p300_pipette.transfer(200, ethanol, target.top(z = -1),
                             new_tip='once')
        protocol_context.delay(seconds = 30)
        p300_pipette.transfer(200, target.bottom(z = 2).move(types.Point(x=-2)), liquid_waste)

    p300_pipette.flow_rate.aspirate = 10

    #14. 10uL-es hegy-el leszívni a maradékot, hegyet kidob.
    #Mélyebbre a hegyet!
    for target in samples:
        #adjusted_location = modify_tip_position(target, general_offset, "bal")
        p20_pipette.transfer(10, target.bottom(z = 1).move(types.Point(x=-2)), liquid_waste, new_tip= "always")


    #15. 3 perc inkubálás mágnesállvánnyal fent
    #Berci
    protocol_context.delay(minutes=0.5)

    #Itt jó lenne, ha csak akkor menne tovább a protokoll, ha én már úgy látom, hogy lehet. (Marci)
    protocol_context.pause("A folytatáshoz nyomja meg a gombot")

    #16. Mágnesállványt le. (=disengage)
    mag_deck.disengage()

    #
    #Berci

    mix_vol = 20
    #17. 22uL AG-MilliQ rámérése. - itt a pellettel megegyező oldalra közelíthet
    #Tehát első sor jobbra, utána váltakozva
    counter = 0
    for target in samples:
        #adjusted_location = modify_tip_position(target, general_offset, "jobb")
        # Berci
        p300_pipette.pick_up_tip()
        p300_pipette.transfer(
            elution_buffer_volume, elution_buffer, target.bottom(z = 2).move(types.Point(x=2)), new_tip='never')
    # 18. 10 alkalommal Fel-le pipettáz 20uL-et, hegyet kidob.
        #Felszívás 2-szer ilyen gyors
        p300_pipette.flow_rate.aspirate = 20
        p300_pipette.mix(10, mix_vol, target.bottom(z = 2).move(types.Point(x=2)))
        p300_pipette.drop_tip()
        
    p300_pipette.flow_rate.aspirate = 10
    #19. Inkubálás 2 percig.
    #Optimalizálásban lehet 30 s
    protocol_context.delay(minutes=0.5)

    #20. Mágnesállványt felemel.
    mag_deck.engage(height_from_base=9)

    #21. Inkubál 3 percig
    protocol_context.delay(minutes=3)

    #23. Áthelyez egy tiszta plate-be. - mehet középre
    row_counter = 0
    for target, dest in zip(samples, output):
        p300_pipette.transfer(elution_buffer_volume, target.bottom(z = 2), dest, blow_out=True, new_tip= "once")
        """row_counter += 1
        protocol_context.comment(str(row_counter))
        if row_counter == len(mag_plate.columns()):
            left_pipette.drop_tip()
            tip_on = False
            row_counter = 0"""
    #24. Hegyet kidob minden sor után

    #25. Mágnesállvány le, plate a kukába.
    mag_deck.disengage()
    #A plate-et nem dobja ki automatikusan
    # On OT-2, you can can only move labware manually, since it doesn’t have a gripper instrument.
