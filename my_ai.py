from pybw_swig import * # import all constants and classes
import pybw

import struct
from collections import namedtuple

class ExAI(object):

    def __init__(self):
        # Add ourselves to the console manager as variable "m"
        pybw.consoleManager.locals.update({'m': self})

    def onConnect(self):
        # Get the game instance
        self.game = getGame()

    def onMatchStart(self):
        sendText("onMatchStart")
        if self.game.isReplay:
            return

        # Get basic information
        self.player = self.game.self
        self.race = self.player.race

        #sendText("%d forces"%len(self.game.getForces()))
        #sendText("%d players"%len(self.game.getPlayers()))
        #sendText("%d accessibleUnits"%len(self.game.getAllUnits()))
        #sendText("%d minerals"%len(self.game.getMinerals()))
        #sendText("%d geysers"%len(self.game.getGeysers()))

        self.resourceAnalysis()

        # Find centers in the beginning
        self.main_centers = [u for u in self.player.units if u.type == self.race.center]

        if self.main_centers:
            self.main_center = self.main_centers[0]

            self.mineral_queue = []
            for mineral in self.minerals:
                distance_to_center = mineral.position.getDistance( self.main_center.position )
                # Only queue workers to get minerals next to the main base
                if distance_to_center < 250:
                    self.mineral_queue.append(( distance_to_center, mineral ))
            self.mineral_queue.sort()

        else:
            self.main_center = None

    def onMatchFrame(self):

        if self.game.isReplay:
            return
        if self.main_center:
            for center_radius in range(1, 10):
                self.game.drawCircle(Map, self.main_center.getPosition().getX(), self.main_center.getPosition().getY(), center_radius * 32,  Color(255 - center_radius*10,0,0))

        self.processIdleUnits()
        self.processProduction()
        self.processCombat()

        # Mark resources
        for mineral in self.minerals:
            self.game.drawBox(Map, mineral.getLeft(), mineral.getTop(), mineral.getRight(), mineral.getBottom(), Blue)
            self.game.drawText(Map, mineral.getPosition().getX(), mineral.getPosition().getY(), "%r" % TilePosition(mineral.getPosition()))

        workers = [u for u in self.player.units if u.type.isWorker]
        self.game.drawTextMouse(0, 0, "%r" % TilePosition(self.game.getMousePosition() + self.game.getScreenPosition()) )
        self.game.drawTextMouse(0, 12, "%r" % self.game.canBuildHere(workers[0], TilePosition(self.game.getMousePosition() + self.game.getScreenPosition()), self.race.center) )

    def onUnitCreate(self, unit):
        if unit.getPlayer() == self.player:
            print("onUnitCreate: %r, Current supply is %d/%d" % (unit, self.player.supplyUsed()/2, self.player.supplyTotal()/2))

    def onUnitMorph(self, unit):
        if unit.getPlayer() == self.player:
            print("onUnitMorph: %r" % unit)

    def onUnitComplete(self, unit):
        if unit.getPlayer() == self.player:
            print("onUnitComplete: %r" % unit)

    def onUnitDestroy(self, unit):
        if unit.getPlayer() == self.player:
            print("onUnitDestroy: %r" % unit)

    def resourceAnalysis(self):
        # Get all resource on the map
        self.minerals = list(self.game.minerals)
        self.geysers = list(self.game.geysers)

    def processIdleUnits(self):
        idle_units = [u for u in self.player.units if u.isIdle and u.isCompleted]
        idle_workers = [u for u in idle_units if u.type.isWorker]

        for u in idle_workers:
            # Go to minerals or geysers
            mineral = self.mineral_queue.pop(0)
            u.gather( mineral[1] )
            self.mineral_queue.append( mineral )
            print("Send worker %d to mineral" % u.getID())

    def processProduction(self):
        #print("processProduction")
        print("Units nearby %d" % len(self.main_center.getUnitsInRadius(288)))
        #workers_near = [u for u in self.game.getUnitsInRadius(self.main_center.getPosition(), 288)]
        #if u.getPlayer() == self.player and u.type.isWorker
        #if len(workers_near) < len(self.mineral_queue) * 2 and self.player.supplyTotal() - self.player.supplyUsed() < 6:
        #    self.main_center.train( self.race.worker )

    def processCombat(self):
        #print("processCombat")
        warrior_units = [u for u in self.player.units if ~u.type.isWorker and u.isCompleted and u.type.canAttack]
        print("Have %d attack units" % len(warrior_units))
