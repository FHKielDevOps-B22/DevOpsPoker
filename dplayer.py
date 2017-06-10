#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#  dodPoker:  a poker server to run automated texas hold'em
#  poker rounds with bots
#  Copyright (C) 2017 wobe-systems GmbH
# -----------------------------------------------------------
# -----------------------------------------------------------
# Configuration
# You need to change the setting according to your environment
gregister_url='http://192.168.0.5:5001'
glocalip_adr='192.168.0.35'

# -----------------------------------------------------------

from flask import Flask, request
from flask_restful import Resource, Api
import sys
import random

from requests import put
import json

app = Flask(__name__)
api = Api(app)

# Web API to be called from the poker manager
class PokerPlayerAPI(Resource):

    ## return bid to caller
    #
    #  Depending on the cards passed to this function in the data parameter,
    #  this function has to return the next bid.
    #  The following rules are applied:
    #   -- fold --
    #   bid < min_bid
    #   bid > max_bid -> ** error **
    #   (bid > min_bid) and (bid < (min_bid+big_blind)) -> ** error **
    #
    #   -- check --
    #   (bid == 0) and (min_bid == 0) -> check
    #
    #   -- call --
    #   (bid == min_bid) and (min_bid > 0)
    #
    #   -- raise --
    #   min_bid + big_blind + x
    #   x is any value to increase on top of the Big blind
    #
    #   -- all in --
    #   bid == max_bid -> all in
    #
    #  @param data : a dictionary containing the following values - example: data['pot']
    #                min_bid   : minimum bid to return to stay in the game
    #                max_bid   : maximum possible bid
    #                big_blind : the current value of the big blind
    #                pot       : the total value of the current pot
    #                board     : a list of board cards on the table as string '<rank><suit>'
    #                hand      : a list of individual hand cards as string '<rank><suit>'
    #
    #                            <rank> : 23456789TJQKA
    #                            <suit> : 's' : spades
    #                                     'h' : hearts
    #                                     'd' : diamonds
    #                                     'c' : clubs
    #
    # @retudatarn a dictionary containing the following values
    #         bid  : a number between 0 and max_bid
    def __get_bid(self, data):
        result = 0
        bigBlind = int(data['big_blind'])
        minBid = int(data['min_bid'])
        maxBid = int(data['max_bid'])
        handList = list(data['hand'])

        boardList = list(data['board'])
        firstHandCard = str(handList[0])
        secondHandCard = str(handList[1])
        #firstBoardCard = str(boardList[0])
        #secondBoardCard = str(boardList[1])
        #thirdBoardCard = str(boardList[2])
        #forthBoardCard = str(boardList[3])
        #fifthBoardCard = str(boardList[4])

        print('dataL ', data)

        if firstHandCard[0] == secondHandCard[0]:
            if ('A', 'K', 'Q', 'J', 'T').__contains__(firstHandCard[0]):
                print("Perfect!")
                result = maxBid
            else:
                raiseValue = (maxBid - minBid)
                print(raiseValue)
                if raiseValue > 100:
                    result = minBid + 20
                else:
                    randomValue = random.randint(0, 1)
                    if randomValue == 1:
                        result = maxBid
                    else:
                        result = minBid
                        print('random: ', randomValue)
        else:
            if firstHandCard[1] == secondHandCard[1]:
                randomValue = random.randint(0, 1)
                if randomValue == 1:
                    result = minBid
                    print('random: ', randomValue)
            else:
                if (firstHandCard[0] == 'A' and secondHandCard[0] == 'K' or firstHandCard[0] == 'K' and secondHandCard[0] == 'A' ) and firstHandCard[1] == secondHandCard[1]:
                    result = maxBid
                else:
                    if ('A', 'K', 'Q', 'J', 'T').__contains__(firstHandCard[0]) and ('A', 'K', 'Q', 'J', 'T').__contains__(secondHandCard[0]):
                        result = maxBid
                    else:
                        if minBid == bigBlind and random.randint(0, 1)==1:
                            result = minBid + 20


        print('result: ',result)
        return result

    # dispatch incoming get commands
    def get(self, command_id):

        data = request.form['data']
        data = json.loads(data)
        #print(self.__get_bid(self.__get_bid(data)))


        if command_id == 'get_bid':
            return {'bid': self.__get_bid(data)}
        else:
            return {}, 201

    # dispatch incoming put commands (if any)
    def put(self, command_id):
        print("put")

        return 201


api.add_resource(PokerPlayerAPI, '/dpoker/player/v1/<string:command_id>')

# main function
def main():

    # run the player bot with parameters
    if len(sys.argv) == 4:
        team_name = sys.argv[1]
        api_port = int(sys.argv[2])
        api_url = 'http://%s:%s' % (glocalip_adr, api_port)
        api_pass = sys.argv[3]
    else:
        print("""
DevOps Poker Bot - usage instruction
------------------------------------
python3 dplayer.py <team name> <port> <password>
example:
    python3 dplayer bazinga 40001 x407
        """)
        return 0

    # register player
    r = put("%s/dpoker/v1/enter_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass':api_pass}).json()
    if r != 201:
        raise Exception('registration failed: probably wrong team name')

    else:
        print('registration successful')

    try:
        app.run(host='0.0.0.0', port=api_port, debug=False)
    finally:
        put("%s/dpoker/v1/leave_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass': api_pass}).json()
# run the main function
if __name__ == '__main__':
    main()


