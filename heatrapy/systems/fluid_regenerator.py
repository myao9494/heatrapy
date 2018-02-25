# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Contains the class magcalsys_solidstate_1D.

Used to compute 1-dimensional models for
magnetocaloric systems

"""

from .. import objects
import time
import numpy as np


class magcalsys_fluidAMR_1D:

    """magcalsys_fluidAMR_1D class
    computes the thermal processes for 1-dimensional AMR systems that uses
    fluids as heat exchanger.
    """

    def __init__(self, fileName, ambTemperature=293, fluid_length=100,
                 MCM_length=20, rightReservoir_length=3,
                 leftReservoir_length=3, MCM_material=((0.04,'Gd'),(0.04,'Cu')),
                 fluid_material='water', leftReservoir_material='Cu',
                 rightReservoir_material='Cu', freq=1., dt=0.001, dx=0.004,
                 stopCriteria=1e-4, solverMode='implicit_k(x)',
                 minCycleNumber=10, maxCycleNumber=2000, cyclePoints=25,
                 note=None, boundaries=((2,0),(3,0)),
                 mode='heat_pump', version=None, 
                 leftHEXpositions=15, rightHEXpositions=15,
                 startingField='magnetization', 
                 temperatureSensor=[3,-3], demagnetizationSteps=5,
                 magnetizationSteps=1, demagnetizationMode='constant_right',
                 magnetizationMode='constant_left',
                 applied_static_field_time_ratio=(0.,0.),removed_static_field_time_ratio=(0.25,0.25),
                 h_mcm_fluid=5000000, h_leftreservoir_fluid=5000000, h_rightreservoir_fluid=5000000,
                 mcm_discontinuity=[2,0.016],#='default'#=[3,0.008]
                 type_study='no load', velocity=.2, mod_freq='default'):#=('/home/daniel/Desktop/freq.txt',10)):

        if startingField=='demagnetization':
            initialState=True
        else:
            initialState=False

        cycle_number = 0
        AMR = objects.system_objects(number_objects=4,
                                    materials=[fluid_material, MCM_material[0][1],
                                                leftReservoir_material,
                                                rightReservoir_material],
                                    objects_length=[fluid_length, MCM_length,
                                                    leftReservoir_length,
                                                    rightReservoir_length],
                                    ambTemperature=293, dx=dx, dt=dt,
                                    fileName=fileName,initialState=initialState,
                                    boundaries=boundaries)

        k=1
        for i in range(len(MCM_material)):
            from .. import mats
            import os
            tadi = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/' + MCM_material[i][1] + '/' + 'tadi.txt'
            tadd = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/' + MCM_material[i][1] + '/' + 'tadd.txt'
            cpa = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/' + MCM_material[i][1] + '/' + 'cpa.txt'
            cp0 = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/' + MCM_material[i][1] + '/' + 'cp0.txt'
            k0 = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/' + MCM_material[i][1] + '/' + 'k0.txt'
            ka = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/' + MCM_material[i][1] + '/' + 'ka.txt'
            rho0 = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/' + MCM_material[i][1] + '/' + 'rho0.txt'
            rhoa = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/' + MCM_material[i][1] + '/' + 'rhoa.txt'
            AMR.objects[1].materials.append(mats.calmatpro(tadi, tadd, cpa, cp0, k0, ka, rho0, rhoa))
            for j in range(k,k+int(MCM_material[i][0]/dx)):
                AMR.objects[1].materialsIndex[j]=len(AMR.objects[1].materials)-1
            k = k+int(MCM_material[i][0]/dx)

        if mcm_discontinuity != 'default':
            from .. import mats
            import os
            tadi = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/vaccum/tadi.txt'
            tadd = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/vaccum/tadd.txt'
            cpa = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/vaccum/cpa.txt'
            cp0 = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/vaccum/cp0.txt'
            k0 = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/vaccum/k0.txt'
            ka = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/vaccum/ka.txt'
            rho0 = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/vaccum/rho0.txt'
            rhoa = os.path.dirname(os.path.realpath(__file__)) + \
                '/../database/vaccum/rhoa.txt'
            AMR.objects[1].materials.append(mats.calmatpro(tadi, tadd, cpa, cp0, k0, ka, rho0, rhoa))

            j=1
            for i in range(1,len(AMR.objects[1].temperature)-1):
                if i < j*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i >= j*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx)):
                    AMR.objects[1].materialsIndex[i]=len(AMR.objects[1].materials)-1
                if i == j*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and j < mcm_discontinuity[0]:
                    j=j+1

        print AMR.objects[1].materialsIndex
        print ''
        print AMR.objects[1].materials
                                
        write_interval = cyclePoints/2
        steps = int(velocity / (2 * freq * dx))
        time_step = (1 / (2. * freq)) / steps

        if int(time_step / dt) == 0:
            print 'dt or frequency too low'
            
        if write_interval > int(time_step / dt):
            write_interval = 1
            
        # information for the log file
        print ''
        print ''
        print '######################################################'
        print ''
        print '------------------------------------------------------'
        print fileName
        print '------------------------------------------------------'
        print ''
        print 'heatconpy version:', version
        print 'Module: magcalsys_fluidAMR_1D'
        if note is not None:
            print ''
            print 'Note:', note
        print ''
        print 'Mode:', mode
        print 'Fluid:', fluid_material+' ('+ str(fluid_length*dx)+')'
        print 'MCM material:', MCM_material
        print 'Left reservoir:', leftReservoir_material+' ('+ str(leftReservoir_length*dx)+')'
        print 'Right reservoir:', rightReservoir_material+' ('+ str(rightReservoir_length*dx)+')'
        print 'Distance between MCM and left HEX:', leftHEXpositions*dx
        print 'Distance between MCM and right HEX:', rightHEXpositions*dx
        print 'dx (m):', dx
        print 'dt (s):', dt
        print 'Frequency (Hz):', freq
        if mcm_discontinuity == 'default':
            print 'Discontinuity: None'
        else:
            print 'Discontinuity:', mcm_discontinuity
        print 'MCM - fluid heat transfer coefficient:', h_mcm_fluid
        print 'Left reservoir - fluid heat transfer coefficient:', h_leftreservoir_fluid
        print 'Right reservoir - fluid heat transfer coefficient:', h_rightreservoir_fluid
        print 'Applied field static time ratios:', applied_static_field_time_ratio
        print 'Removed field static time ratios:', removed_static_field_time_ratio
        print 'Solver:', solverMode
        print 'Magnetization mode:', magnetizationMode
        print 'Magnetization steps:', magnetizationSteps
        print 'Demagnetization mode:', demagnetizationMode
        print 'Demagnetization steps:', demagnetizationSteps
        print 'Starting Field:', startingField
        print 'Boundaries:', boundaries
        print 'Ambient temperature (K):', ambTemperature
        print 'Stop criteria:', stopCriteria
        print 'Time:', time.ctime()
        print ''

        startTime = time.time()

        if type_study == 'no load':

            value1 = AMR.objects[0].temperature[temperatureSensor[0]][0]
            value2 = AMR.objects[0].temperature[temperatureSensor[1]][0]

            if startingField=='magnetization':

                condition = True
                while condition:

                    value1 = AMR.objects[0].temperature[temperatureSensor[0]][0]
                    value2 = AMR.objects[0].temperature[temperatureSensor[1]][0]

                    if mod_freq != 'default':
                        temperature_sensor = AMR.objects[1].temperature[mod_freq[1]][0]
                        input = open(mod_freq[0], 'r')
                        s = input.readlines()
                        xMod = []
                        yMod = []
                        for line in s:
                            pair = line.split(',')
                            xMod.append(float(pair[0]))
                            yMod.append(float(pair[1]))
                        input.close()
                        freq = np.interp(temperature_sensor, xMod, yMod)
                        print freq, AMR.objects[1].temperature[mod_freq[1]][0]
                        steps = int(velocity / (2 * freq * dx))
                        time_step = (1 / (2. * freq)) / steps
                        if int(time_step / dt) == 0:
                            print 'dt or frequency too low'                         
                        if write_interval > int(time_step / dt):
                            write_interval = 1

                    #MAGNETIZATION

                    j=0
                    time_passed = 0.
                    if magnetizationMode == 'constant_left' or magnetizationMode == 'accelerated_left' or magnetizationMode == 'decelerated_left':
                        j=magnetizationSteps - 1

                    for n in range(steps):

                        #contacts
                        contacts = set()

                        init_pos = fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                        for i in range(leftReservoir_length):
                            contacts.add(((0, i+n+init_pos), (2, i+1), h_leftreservoir_fluid))

                        if mcm_discontinuity == 'default':
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                            for i in range(MCM_length):
                                contacts.add(((0, i+init_pos+n), (1, i+1), h_mcm_fluid))
                        else:
                            p=1
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                            for i in range(MCM_length):
                                if not (i+1 < p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i+1 >= p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx))):
                                    contacts.add(((0, i+init_pos+n), (1, i+1), h_mcm_fluid))
                                if i+1 == p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and p < mcm_discontinuity[0]:
                                    p=p+1

                        init_pos = leftReservoir_length+leftHEXpositions+rightHEXpositions+MCM_length+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                        for i in range(rightReservoir_length):
                            contacts.add(((0, i+init_pos+n), (3, i+1), h_rightreservoir_fluid))

                        AMR.contacts = contacts


                        if n*time_step < applied_static_field_time_ratio[0]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        elif n*time_step > 1/(2.*freq) - applied_static_field_time_ratio[1]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)
                        else:

                            #MCE

                            #MODE 1
                            if magnetizationMode == 'constant_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 2
                            if magnetizationMode == 'accelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False
                            
                            #MODE 3
                            if magnetizationMode == 'decelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 4
                            if magnetizationMode == 'constant_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 5
                            if magnetizationMode == 'accelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 6
                            if magnetizationMode == 'decelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                    #DEMAGNETIZATION

                    j=0
                    time_passed = 0.
                    if demagnetizationMode == 'constant_left' or demagnetizationMode == 'accelerated_left' or demagnetizationMode == 'decelerated_left':
                        j=demagnetizationSteps - 1

                    for n in range(steps):

                        #contacts
                        contacts = set()

                        init_pos = fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                        for i in range(leftReservoir_length):
                            contacts.add(((0, i+init_pos-n), (2, i+1), h_leftreservoir_fluid))

                        if mcm_discontinuity == 'default':
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                            for i in range(MCM_length):
                                contacts.add(((0, i+init_pos-n), (1, i+1), h_mcm_fluid))
                        else:
                            p=1
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                            for i in range(MCM_length):
                                if not (i+1 < p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i+1 >= p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx))):
                                    contacts.add(((0, i+init_pos-n), (1, i+1), h_mcm_fluid))
                                if i+1 == p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and p < mcm_discontinuity[0]:
                                    p=p+1

                        init_pos = leftReservoir_length+leftHEXpositions+rightHEXpositions+MCM_length+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                        for i in range(rightReservoir_length):
                            contacts.add(((0, i+init_pos-n), (3, i+1), h_rightreservoir_fluid))

                        AMR.contacts = contacts
                        #print AMR.contactFilter(1)
                        #print AMR.objects[1].materialsIndex

                        if n*time_step < removed_static_field_time_ratio[0]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        elif n*time_step > 1/(2.*freq) - removed_static_field_time_ratio[1]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)
                        else:

                            #MCE

                            #MODE 1
                            if demagnetizationMode == 'constant_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 2
                            if demagnetizationMode == 'accelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False
                            
                            #MODE 3
                            if demagnetizationMode == 'decelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 4
                            if demagnetizationMode == 'constant_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 5
                            if demagnetizationMode == 'accelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 6
                            if demagnetizationMode == 'decelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                    if value1 == value2:
                        condition = True
                    else:
                        condition = (cycle_number < minCycleNumber or (abs(abs(AMR.objects[2].temperature[leftReservoir_length/2][0]-AMR.objects[3].temperature[rightReservoir_length/2][0]) - abs(value1-value2)))/abs(value1-value2) > stopCriteria) and cycle_number<maxCycleNumber

                    cycle_number = cycle_number + 1

            elif startingField=='demagnetization':
                condition = True
                while condition:

                    value1 = AMR.objects[0].temperature[temperatureSensor[0]][0]
                    value2 = AMR.objects[0].temperature[temperatureSensor[1]][0]

                    if mod_freq != 'default':
                        temperature_sensor = AMR.objects[1].temperature[mod_freq[1]][0]
                        input = open(mod_freq[0], 'r')
                        s = input.readlines()
                        xMod = []
                        yMod = []
                        for line in s:
                            pair = line.split(',')
                            xMod.append(float(pair[0]))
                            yMod.append(float(pair[1]))
                        input.close()
                        freq = np.interp(temperature_sensor, xMod, yMod)
                        steps = int(velocity / (2 * freq * dx))
                        time_step = (1 / (2. * freq)) / steps
                        if int(time_step / dt) == 0:
                            print 'dt or frequency too low'                         
                        if write_interval > int(time_step / dt):
                            write_interval = 1

                    j=0
                    time_passed = 0.
                    if demagnetizationMode == 'constant_left' or demagnetizationMode == 'accelerated_left' or demagnetizationMode == 'decelerated_left':
                        j=demagnetizationSteps - 1

                    for n in range(steps):

                        #contacts
                        contacts = set()

                        init_pos = fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                        for i in range(leftReservoir_length):
                            contacts.add(((0, i+init_pos-n), (2, i+1), h_leftreservoir_fluid))

                        if mcm_discontinuity == 'default':
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                            for i in range(MCM_length):
                                contacts.add(((0, i+init_pos-n), (1, i+1), h_mcm_fluid))
                        else:
                            p=1
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                            for i in range(MCM_length):
                                if not (i+1 < p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i+1 >= p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx))):
                                    contacts.add(((0, i+init_pos-n), (1, i+1), h_mcm_fluid))
                                if i+1 == p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and p < mcm_discontinuity[0]:
                                    p=p+1

                        init_pos = leftReservoir_length+leftHEXpositions+rightHEXpositions+MCM_length+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                        for i in range(rightReservoir_length):
                            contacts.add(((0, i+init_pos-n), (3, i+1), h_rightreservoir_fluid))

                        AMR.contacts = contacts

                        if n*time_step < removed_static_field_time_ratio[0]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        elif n*time_step > 1/(2.*freq) - removed_static_field_time_ratio[1]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)
                        else:

                            #MCE

                            #MODE 1
                            if demagnetizationMode == 'constant_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 2
                            if demagnetizationMode == 'accelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False
                            
                            #MODE 3
                            if demagnetizationMode == 'decelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 4
                            if demagnetizationMode == 'constant_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 5
                            if demagnetizationMode == 'accelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 6
                            if demagnetizationMode == 'decelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                    #MAGNETIZATION
                    j=0
                    time_passed = 0.
                    if magnetizationMode == 'constant_left' or magnetizationMode == 'accelerated_left' or magnetizationMode == 'decelerated_left':
                        j=magnetizationSteps - 1

                    for n in range(steps):

                        #contacts
                        contacts = set()

                        init_pos = fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                        for i in range(leftReservoir_length):
                            contacts.add(((0, i+n+init_pos), (2, i+1), h_rightreservoir_fluid))

                        if mcm_discontinuity == 'default':
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                            for i in range(MCM_length):
                                contacts.add(((0, i+init_pos+n), (1, i+1), h_mcm_fluid))
                        else:
                            p=1
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                            for i in range(MCM_length):
                                if not (i+1 < p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i+1 >= p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx))):
                                    contacts.add(((0, i+init_pos+n), (1, i+1), h_mcm_fluid))
                                if i+1 == p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and p < mcm_discontinuity[0]:
                                    p=p+1

                        init_pos = leftReservoir_length+leftHEXpositions+rightHEXpositions+MCM_length+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                        for i in range(rightReservoir_length):
                            contacts.add(((0, i+init_pos+n), (3, i+1), h_leftreservoir_fluid))

                        AMR.contacts = contacts
                        
                        if n*time_step < applied_static_field_time_ratio[0]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        elif n*time_step > 1/(2.*freq) - applied_static_field_time_ratio[1]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        else:

                            #MCE

                            #MODE 1
                            if magnetizationMode == 'constant_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 2
                            if magnetizationMode == 'accelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False
                            
                            #MODE 3
                            if magnetizationMode == 'decelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 4
                            if magnetizationMode == 'constant_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 5
                            if magnetizationMode == 'accelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 6
                            if magnetizationMode == 'decelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                    if value1 == value2:
                        condition = True
                    else:
                        condition = (cycle_number < minCycleNumber or (abs(abs(AMR.objects[2].temperature[leftReservoir_length/2][0]-AMR.objects[3].temperature[rightReservoir_length/2][0]) - abs(value1-value2)))/abs(value1-value2) > stopCriteria) and cycle_number<maxCycleNumber

                    cycle_number = cycle_number + 1

            else:
                print 'incorrect startingField'


            if startingField=='magnetization' or startingField=='demagnetization':
                endTime = time.time()
                simulationTime = endTime - startTime
                hours = int(simulationTime / 3600)
                minutes = int((simulationTime - hours * 3600) / 60)
                seconds = int(simulationTime - hours * 3600 - (minutes * 60))
                hours = '%02d' % hours
                minutes = '%02d' % minutes
                seconds = '%02d' % seconds

                print '------------------------------------------------------'
                print ''
                print 'Number of cycles:', cycle_number
                print 'Final cycle error:', (abs(abs(AMR.objects[2].temperature[leftReservoir_length/2][0]-AMR.objects[3].temperature[rightReservoir_length/2][0]) - abs(value1-value2)))#/abs(value1-value2)
                if mode == 'refrigerator':
                    if type_study == 'no load':
                        temperature_span = abs(AMR.objects[2].temperature[leftReservoir_length/2][0]-AMR.objects[3].temperature[rightReservoir_length/2][0])
                        print 'No load temperature span (K):', temperature_span
                    if type_study == 'fixed temperature span':
                        cooling_power = (-AMR.q2+q2)*freq
                        working_power = (AMR.q2-q2+AMR.q1-q1)*freq
                        COP = cooling_power/working_power
                        print 'Cooling power (W):', cooling_power
                        print 'Working power (W)', working_power
                        print 'COP:', COP
                if mode == 'heat_pump':
                    if type_study == 'no load':
                        temperature_span = abs(AMR.objects[2].temperature[leftReservoir_length/2][0]-AMR.objects[3].temperature[rightReservoir_length/2][0])
                        print 'No load temperature span (K):', temperature_span
                    if type_study == 'fixed temperature span':
                        heating_power = (AMR.q1-q1)*freq
                        working_power = (AMR.q2-q2+AMR.q1-q1)*freq
                        print 'Heating power (W):', heating_power
                        print 'Working power (W)', working_power
                        print 'COP:', heating_power/working_power
                print 'Final time (s):', AMR.objects[0].timePassed
                print 'Simulation duration:', hours + ':' + minutes + ':' + seconds
                print ''
                print '------------------------------------------------------'
                print ''
                print ''
                print ''

            else:
                print 'simulation not complete'



        if type_study == 'fixed temperature span':

            value1 = AMR.objects[2].Q0[leftReservoir_length/2]

            if startingField=='magnetization':

                condition = True

                while condition:

                    value1 = AMR.objects[2].Q0[leftReservoir_length/2]
                    q1 = AMR.q1
                    q2 = AMR.q2

                    if mod_freq != 'default':
                        temperature_sensor = AMR.objects[1].temperature[mod_freq[1]][0]
                        input = open(mod_freq[0], 'r')
                        s = input.readlines()
                        xMod = []
                        yMod = []
                        for line in s:
                            pair = line.split(',')
                            xMod.append(float(pair[0]))
                            yMod.append(float(pair[1]))
                        input.close()
                        freq = np.interp(temperature_sensor, xMod, yMod)
                        steps = int(velocity / (2 * freq * dx))
                        time_step = (1 / (2. * freq)) / steps
                        if int(time_step / dt) == 0:
                            print 'dt or frequency too low'                         
                        if write_interval > int(time_step / dt):
                            write_interval = 1#int(time_step / dt)

                    #MAGNETIZATION

                    j=0
                    time_passed = 0.
                    if magnetizationMode == 'constant_left' or magnetizationMode == 'accelerated_left' or magnetizationMode == 'decelerated_left':
                        j=magnetizationSteps - 1

                    for n in range(steps):

                        #contacts
                        contacts = set()

                        init_pos = fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                        for i in range(leftReservoir_length):
                            contacts.add(((0, i+n+init_pos), (2, i+1), h_leftreservoir_fluid))

                        if mcm_discontinuity == 'default':
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                            for i in range(MCM_length):
                                contacts.add(((0, i+init_pos+n), (1, i+1), h_mcm_fluid))
                        else:
                            p=1
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                            for i in range(MCM_length):
                                if not (i+1 < p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i+1 >= p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx))):
                                    contacts.add(((0, i+init_pos+n), (1, i+1), h_mcm_fluid))
                                if i+1 == p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and p < mcm_discontinuity[0]:
                                    p=p+1

                        init_pos = leftReservoir_length+leftHEXpositions+rightHEXpositions+MCM_length+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                        for i in range(rightReservoir_length):
                            contacts.add(((0, i+init_pos+n), (3, i+1), h_rightreservoir_fluid))

                        AMR.contacts = contacts

                        if n*time_step < applied_static_field_time_ratio[0]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        elif n*time_step > 1/(2.*freq) - applied_static_field_time_ratio[1]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)
                        else:

                            #MCE

                            #MODE 1
                            if magnetizationMode == 'constant_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 2
                            if magnetizationMode == 'accelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False
                            
                            #MODE 3
                            if magnetizationMode == 'decelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 4
                            if magnetizationMode == 'constant_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 5
                            if magnetizationMode == 'accelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 6
                            if magnetizationMode == 'decelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                    #DEMAGNETIZATION

                    j=0
                    time_passed = 0.
                    if demagnetizationMode == 'constant_left' or demagnetizationMode == 'accelerated_left' or demagnetizationMode == 'decelerated_left':
                        j=demagnetizationSteps - 1

                    for n in range(steps):

                        #contacts
                        contacts = set()

                        init_pos = fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                        for i in range(leftReservoir_length):
                            contacts.add(((0, i+init_pos-n), (2, i+1), h_leftreservoir_fluid))

                        if mcm_discontinuity == 'default':
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                            for i in range(MCM_length):
                                contacts.add(((0, i+init_pos-n), (1, i+1), h_mcm_fluid))
                        else:
                            p=1
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                            for i in range(MCM_length):
                                if not (i+1 < p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i+1 >= p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx))):
                                    contacts.add(((0, i+init_pos-n), (1, i+1), h_mcm_fluid))
                                if i+1 == p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and p < mcm_discontinuity[0]:
                                    p=p+1

                        init_pos = leftReservoir_length+leftHEXpositions+rightHEXpositions+MCM_length+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                        for i in range(rightReservoir_length):
                            contacts.add(((0, i+init_pos-n), (3, i+1), h_rightreservoir_fluid))

                        AMR.contacts = contacts

                        if n*time_step < removed_static_field_time_ratio[0]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        elif n*time_step > 1/(2.*freq) - removed_static_field_time_ratio[1]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)
                        else:

                            #MCE

                            #MODE 1
                            if demagnetizationMode == 'constant_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 2
                            if demagnetizationMode == 'accelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False
                            
                            #MODE 3
                            if demagnetizationMode == 'decelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 4
                            if demagnetizationMode == 'constant_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 5
                            if demagnetizationMode == 'accelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 6
                            if demagnetizationMode == 'decelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                    condition = (cycle_number < minCycleNumber or abs(AMR.objects[2].Q0[leftReservoir_length/2]-value1)/value1 > stopCriteria) and cycle_number<maxCycleNumber
                    cycle_number = cycle_number + 1
                
            elif startingField=='demagnetization':
                condition = True
                while condition:

                    value1 = AMR.objects[2].Q0[leftReservoir_length/2]
                    q1 = AMR.q1
                    q2 = AMR.q2

                    if mod_freq != 'default':
                        temperature_sensor = AMR.objects[1].temperature[mod_freq[1]][0]
                        input = open(mod_freq[0], 'r')
                        s = input.readlines()
                        xMod = []
                        yMod = []
                        for line in s:
                            pair = line.split(',')
                            xMod.append(float(pair[0]))
                            yMod.append(float(pair[1]))
                        input.close()
                        freq = np.interp(temperature_sensor, xMod, yMod)
                        steps = int(velocity / (2 * freq * dx))
                        time_step = (1 / (2. * freq)) / steps
                        if int(time_step / dt) == 0:
                            print 'dt or frequency too low'                         
                        if write_interval > int(time_step / dt):
                            write_interval = 1

                    j=0
                    time_passed = 0.
                    if demagnetizationMode == 'constant_left' or demagnetizationMode == 'accelerated_left' or demagnetizationMode == 'decelerated_left':
                        j=demagnetizationSteps - 1

                    for n in range(steps):

                        #contacts
                        contacts = set()

                        init_pos = fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                        for i in range(leftReservoir_length):
                            contacts.add(((0, i+init_pos-n), (2, i+1), h_leftreservoir_fluid))

                        if mcm_discontinuity == 'default':
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                            for i in range(MCM_length):
                                contacts.add(((0, i+init_pos-n), (1, i+1), h_mcm_fluid))
                        else:
                            p=1
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                            for i in range(MCM_length):
                                if not (i+1 < p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i+1 >= p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx))):
                                    contacts.add(((0, i+init_pos-n), (1, i+1), h_mcm_fluid))
                                if i+1 == p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and p < mcm_discontinuity[0]:
                                    p=p+1

                        init_pos = leftReservoir_length+leftHEXpositions+rightHEXpositions+MCM_length+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 + steps/2
                        for i in range(rightReservoir_length):
                            contacts.add(((0, i+init_pos-n), (3, i+1), h_rightreservoir_fluid))

                        AMR.contacts = contacts

                        #compute
                        #AMR.compute(time_step,write_interval)

                        if n*time_step < removed_static_field_time_ratio[0]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        elif n*time_step > 1/(2.*freq) - removed_static_field_time_ratio[1]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)
                        else:

                            #MCE

                            #MODE 1
                            if demagnetizationMode == 'constant_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 2
                            if demagnetizationMode == 'accelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False
                            
                            #MODE 3
                            if demagnetizationMode == 'decelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < demagnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 4
                            if demagnetizationMode == 'constant_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = time_interval = ((1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1]) * 1 / (2. * freq)) / demagnetizationSteps
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 5
                            if demagnetizationMode == 'accelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(demagnetizationSteps - j) - np.sqrt(demagnetizationSteps - j - 1)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 6
                            if demagnetizationMode == 'decelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==demagnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < demagnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < demagnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - removed_static_field_time_ratio[0] - removed_static_field_time_ratio[1])) * freq * np.sqrt(demagnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / demagnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / demagnetizationSteps + 1)
                                            AMR.objects[1].deactivate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                    #MAGNETIZATION
                    j=0
                    time_passed = 0.
                    if magnetizationMode == 'constant_left' or magnetizationMode == 'accelerated_left' or magnetizationMode == 'decelerated_left':
                        j=magnetizationSteps - 1

                    for n in range(steps):

                        #contacts
                        contacts = set()

                        init_pos = fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                        for i in range(leftReservoir_length):
                            contacts.add(((0, i+n+init_pos), (2, i+1), h_leftreservoir_fluid))

                        if mcm_discontinuity == 'default':
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                            for i in range(MCM_length):
                                contacts.add(((0, i+init_pos+n), (1, i+1), h_mcm_fluid))
                        else:
                            p=1
                            init_pos = leftReservoir_length+leftHEXpositions+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                            for i in range(MCM_length):
                                if not (i+1 < p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx))  and i+1 >= p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)-int(mcm_discontinuity[1]/(2*dx))):
                                    contacts.add(((0, i+init_pos+n), (1, i+1), h_mcm_fluid))
                                if i+1 == p*len(AMR.objects[1].temperature)/(mcm_discontinuity[0]+1)+int(mcm_discontinuity[1]/(2*dx)) and p < mcm_discontinuity[0]:
                                    p=p+1

                        init_pos = leftReservoir_length+leftHEXpositions+rightHEXpositions+MCM_length+fluid_length / 2 - (leftReservoir_length+leftHEXpositions+MCM_length+rightHEXpositions+rightReservoir_length) / 2 - steps/2
                        for i in range(rightReservoir_length):
                            contacts.add(((0, i+init_pos+n), (3, i+1), h_rightreservoir_fluid))

                        AMR.contacts = contacts
                        
                        if n*time_step < applied_static_field_time_ratio[0]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)

                        elif n*time_step > 1/(2.*freq) - applied_static_field_time_ratio[1]/2:
                            AMR.compute(time_step, write_interval, solver=solverMode)
                        else:

                            #MCE

                            #MODE 1
                            if magnetizationMode == 'constant_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 2
                            if magnetizationMode == 'accelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False
                            
                            #MODE 3
                            if magnetizationMode == 'decelerated_right':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==0:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j+1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j < magnetizationSteps:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 4
                            if magnetizationMode == 'constant_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = time_interval = ((1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1]) * 1 / (2. * freq)) / magnetizationSteps
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 5
                            if magnetizationMode == 'accelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(magnetizationSteps - j) - np.sqrt(magnetizationSteps - j - 1)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                            #MODE 6
                            if magnetizationMode == 'decelerated_left':
                                cond = True
                                previous_time=0.
                                flag = True
                                if j==magnetizationSteps - 1:
                                    time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                while cond:
                                    if (time_interval-time_passed) > time_step:
                                        if time_passed==0. and j < magnetizationSteps:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                        else:
                                            delta_t = time_step
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        time_passed = time_passed + delta_t
                                        cond = False
                                        flag=True
                                    else:
                                        if time_passed==0. and j < magnetizationSteps and flag:
                                            time_interval = ((1 / (2 * (1. / (1. - applied_static_field_time_ratio[0] - applied_static_field_time_ratio[1])) * freq * np.sqrt(magnetizationSteps))) * (np.sqrt(j + 1) - np.sqrt(j)))
                                            first = (j * MCM_length / magnetizationSteps + 1)
                                            second = ((j+1) * MCM_length / magnetizationSteps + 1)
                                            AMR.objects[1].activate(first, second)
                                            j=j-1
                                            delta_t = time_step-previous_time
                                            flag = False
                                            time_passed = delta_t
                                        else:
                                            delta_t = time_interval-time_passed
                                            time_passed = 0.
                                            flag=True
                                        previous_time = delta_t
                                        AMR.compute(delta_t, write_interval, solver=solverMode)
                                        if j >= 0:
                                            cond = True
                                        else:
                                            cond = False

                    condition = (cycle_number < minCycleNumber or abs(AMR.objects[2].Q0[leftReservoir_length/2]-value1)/value1 > stopCriteria) and cycle_number<maxCycleNumber

                    cycle_number = cycle_number + 1

            else:
                print 'incorrect startingField'


            if startingField=='magnetization' or startingField=='demagnetization':

                endTime = time.time()
                simulationTime = endTime - startTime
                hours = int(simulationTime / 3600)
                minutes = int((simulationTime - hours * 3600) / 60)
                seconds = int(simulationTime - hours * 3600 - (minutes * 60))
                hours = '%02d' % hours
                minutes = '%02d' % minutes
                seconds = '%02d' % seconds

                print '------------------------------------------------------'
                print ''
                print 'Number of cycles:', cycle_number
                print 'Final cycle error:', abs(AMR.objects[2].Q0[leftReservoir_length/2]-value1)/value1
                if mode == 'refrigerator':
                    if type_study == 'no load':
                        temperature_span = abs(AMR.objects[2].temperature[leftReservoir_length/2][0]-AMR.objects[3].temperature[rightReservoir_length/2][0])
                        print 'No load temperature span (K):', temperature_span
                    if type_study == 'fixed temperature span':
                        cooling_power = (-AMR.q2+q2)/freq
                        working_power = (AMR.q2-q2+AMR.q1-q1)/freq
                        COP = cooling_power/working_power
                        print 'Cooling power (W):', cooling_power
                        print 'Working power (W)', working_power
                        print 'COP:', COP
                if mode == 'heat_pump':
                    if type_study == 'no load':
                        temperature_span = abs(AMR.objects[2].temperature[leftReservoir_length/2][0]-AMR.objects[3].temperature[rightReservoir_length/2][0])
                        print 'No load temperature span (K):', temperature_span
                    if type_study == 'fixed temperature span':
                        heating_power = (AMR.q1-q1)/freq
                        working_power = (AMR.q2-q2+AMR.q1-q1)/freq
                        print 'Heating power (W):', heating_power
                        print 'Working power (W)', working_power
                        print 'COP:', heating_power/working_power
                print 'Final time (s):', AMR.objects[0].timePassed
                print 'Simulation duration:', hours + ':' + minutes + ':' + seconds
                print ''
                print '------------------------------------------------------'
                print ''
                print ''
                print ''

            else:
                print 'simulation not complete'