from otp.ai.AIBase import *
from toontown.toonbase import ToontownGlobals
from direct.distributed.ClockDelta import *
from toontown.building.ElevatorConstants import *
from toontown.building import DistributedElevatorExtAI
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.task import Task
import CogDisguiseGlobals

class DistributedLawOfficeElevatorExtAI(DistributedElevatorExtAI.DistributedElevatorExtAI):

    def __init__(self, air, bldg, officeId, entranceId, antiShuffle = 0, minLaff = 0):
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(self, air, bldg, antiShuffle=antiShuffle, minLaff=minLaff)
        self.officeId = officeId
        self.cogDept = ToontownGlobals.cogHQZoneId2deptIndex(self.officeId)
        self.type = ELEVATOR_OFFICE
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.entranceId = entranceId

    def getEntranceId(self):
        return self.entranceId
        
    def getOfficeId(self):
        return self.officeId

    def avIsOKToBoard(self, av):
        if not DistributedElevatorExtAI.DistributedElevatorExtAI.avIsOKToBoard(self, av):
            return False
        return True

    def elevatorClosed(self):
        numPlayers = self.countFullSeats()
        if numPlayers > 0:
            players = []
            for i in self.seats:
                if i not in [None, 0]:
                    players.append(i)

            officeZone = self.bldg.createOffice(self.officeId, self.entranceId, players)
            for seatIndex in range(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setOfficeInteriorZone', [officeZone])
                    self.clearFullNow(seatIndex)

        else:
            self.notify.warning('The elevator left, but was empty.')
        self.fsm.request('closed')
        return

    def enterClosed(self):
        DistributedElevatorExtAI.DistributedElevatorExtAI.enterClosed(self)
        self.fsm.request('opening')

    def sendAvatarsToDestination(self, avIdList):
        if len(avIdList) > 0:
            officeZone = self.bldg.createOffice(self.officeId, avIdList)
            for avId in avIdList:
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setOfficeInteriorZoneForce', [officeZone])

