__author__ = 'manuelli'
import numpy as np
from sarsa import SARSA

class PolicySearchREINFORCE(PolicySearch):

    def __init__(self, numInnerBins=4, numOuterBins=4, binCutoff=0.5, alphaStepSize=0.2,
                 useQLearningUpdate= False, **kwargs):

        PolicySearch.__init__(self, alphaStepSize=0.2, **kwargs)

        self.numInnerBins=numInnerBins
        self.numOuterBins=numOuterBins
        self.numBins=numInnerBins + numOuterBins
        self.binCutoff=binCutoff
        self.initializeBinData()

    def computeDummyControlPolicy(self, S, randomize=True, counter=None):
        actionIdx = 1                  # hardcoded to go straight, for debugging
        u = self.actionSet[actionIdx]

        if randomize:
            if counter is not None:
                epsilon = self.epsilonGreedyDecay(counter)
            else:
                epsilon = self.epsilonGreedy

            if np.random.uniform(0,1,1)[0] < epsilon:
                # otherActionIdx = np.setdiff1d(self.actionSetIdx, np.array([actionIdx]))
                # randActionIdx = np.random.choice(otherActionIdx)
                actionIdx = np.random.choice(self.actionSetIdx)
                u = self.actionSet[actionIdx]

        return u, actionIdx
        

    def initializeBinData(self):
        self.binData = ()

        innerBinRays = self.computeBinRayIdx(self.numInnerBins)
        for idx in xrange(self.numInnerBins):
            d = dict()
            d['type'] = "inner"
            d['idx'] = idx
            d['rayIdx'] = innerBinRays[idx]
            d['minRange'] = self.collisionThreshold
            d['maxRange'] = self.collisionThreshold + (self.rayLength - self.collisionThreshold)*self.binCutoff
            self.binData+=(d,)

        outerBinRays = self.computeBinRayIdx(self.numOuterBins)
        for idx in xrange(self.numOuterBins):
            d = dict()
            d['type'] = "outer"
            d['idx'] = idx
            d['rayIdx'] = innerBinRays[idx]
            d['minRange'] = self.collisionThreshold + (self.rayLength - self.collisionThreshold)*self.binCutoff
            d['maxRange'] = self.rayLength - self.tol
            self.binData+=(d,)


    def computeBinRayIdx(self, numBins):
        if numBins==0:
            return 0
        binRays = ()
        cutoffs = np.floor(np.linspace(0,self.numRays,numBins+1))
        for idx in xrange(numBins):
            rayLeftIdx = cutoffs[idx]
            rayRightIdx = cutoffs[idx+1]-1
            if idx==numBins-1:
                rayRightIdx=self.numRays
            binRays+=(np.arange(rayLeftIdx,rayRightIdx, dtype='int'),)

        return binRays

    def computeBinOccupied(self,raycastDistance, binNum):
        occupied=0
        minRange = self.binData[binNum]['minRange']
        maxRange = self.binData[binNum]['maxRange']
        rayIdx = self.binData[binNum]['rayIdx']
        if (np.any(np.logical_and(raycastDistance[rayIdx] > minRange, raycastDistance[rayIdx] < maxRange) ) ):
            occupied = 1

        return occupied


    def computeFeatureVector(self,S,A_idx=None):
        raycastDistance = S[1]
        featureTuple = ()
        for idx in xrange(self.numBins):
            featureTuple+= (self.computeBinOccupied(raycastDistance, idx),)


        if A_idx is not None:
            featureTuple += (A_idx,)

        return featureTuple


    def deleteKeysFromDict(self, d, keys):
        for key in keys:
            if key in d:
                del d[key]



    def computeFeatureVectorFromCurrentFrame(self):
        raycastDistance = self.sensor.raycastAllFromCurrentFrameLocation()
        carState = 0
        S = (carState, raycastDistance)
        featureVec = self.computeFeatureVector(S)
        print ""
        print "innerBins ", featureVec[:self.numInnerBins]
        print "outerBins", featureVec[self.numInnerBins:]
        print ""
        return featureVec


    def computeQValueVectorFromCurrentFrame(self):
        QVec = np.zeros(3)
        fVec = self.computeFeatureVectorFromCurrentFrame()
        for aIdx in xrange(self.numActions):
            fVecTemp = fVec + (aIdx,)
            QVec[aIdx] = self.QValues[fVecTemp]


        print "QVec is", QVec
        aIdxMax = np.argmax(QVec)
        if QVec[aIdxMax] == 0.0:
            print "table value never updated"
        else:
            print "best action is", aIdxMax




