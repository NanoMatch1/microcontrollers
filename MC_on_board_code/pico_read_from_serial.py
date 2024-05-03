while True:
    if select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.readline()
        ch = ch.strip()
        command = ch.split(' ')
        print('Pico received {}'.format(ch))
    else:
        time.sleep(0.01)
        continue

    if command[0].strip() == 'light':
        try:
            duty = float(command[1].strip())

            if duty > 100:
                duty = 100
            elif duty < 0:
                duty = 0

        except ValueError:
            print('{} not recognized as a number. Please enter a number from 0-100'.format(command[1]))
            continue  # Skip further processing for invalid commands

        duty = (duty / 100) * 65535
        duty = int(round(duty))
        lightPin.duty_u16(duty)
        lightPin2.duty_u16(duty)
    else:
        command = ch
        #unrecognized_command = ' '.join(command)
        #print('{} not recognized'.format(unrecognized_command))

        # Send the unrecognized command over UART to the G-code controller
        print('pico wrote {}'.format(command))
        uart.write(command + '\r\n')  # Assuming commands should be terminated with a newline

