#! /usr/bin/env python3

from __future__ import print_function
import sys
from optparse import OptionParser
import random

# to make Python2 and Python3 act the same -- how dumb
def random_seed(seed):
    try:
        random.seed(seed, version=1)


    except:
        random.seed(seed)
    return

parser = OptionParser()
parser.add_option("-s", "--seed", default=0, help="the random seed", action="store", type="int", dest="seed")
parser.add_option("-j", "--jobs", default=3, help="number of jobs in the system", action="store", type="int", dest="jobs")
parser.add_option("-l", "--jlist", default="", help="instead of random jobs, provide a comma-separated list of run times", action="store", type="string", dest="jlist")
parser.add_option("-m", "--maxlen", default=10, help="max length of job", action="store", type="int", dest="maxlen")
parser.add_option("-p", "--policy", default="FIFO", help="sched policy to use: SJF, FIFO, RR", action="store", type="string", dest="policy")
parser.add_option("-q", "--quantum", help="length of time slice for RR policy", default=1, action="store", type="int", dest="quantum")
parser.add_option("-c", help="compute answers for me", action="store_true", default=False, dest="solve")

#--------------------------------------------------------------
# 각 job의 arrivaltime을 설정할 수 있도록 option을 추가하였다.
# 또한 arrivaltime을 랜덤하게 생성할 경우 그 최대값을 설정할 수 있도록 option을 추가하였다.
parser.add_option("-a", "--arrivaltime", default="", help="instead of random jobs, a comma-separated list of arrival times", action="store", type="string", dest="alist")
parser.add_option("-b", "--maxarrivaltime", default=20, help="max arrival time of job", action="store", type="int", dest="mat")
#--------------------------------------------------------------

(options, args) = parser.parse_args()

random_seed(options.seed)

print('ARG policy', options.policy)
if options.jlist == '':
    print('ARG jobs', options.jobs)
    print('ARG maxlen', options.maxlen)
    print('ARG maxarrivaltime', options.mat)
    print('ARG seed', options.seed)
else:
    print('ARG jlist', options.jlist)
print('')

print('Here is the job list, with the run time of each job: ')

import operator

# joblist = []
# if options.jlist == '':
#     for jobnum in range(0,options.jobs):
#         runtime = int(options.maxlen * random.random()) + 1
#         joblist.append([jobnum, runtime])
#         print('  Job', jobnum, '( length = ' + str(runtime) + ' )')
# else:
#     jobnum = 0
#     for runtime in options.jlist.split(','):
#         joblist.append([jobnum, float(runtime)])
#         jobnum += 1
#     for job in joblist:
#         print('  Job', job[0], '( length = ' + str(job[1]) + ' )')


joblist = []
arrivaltime = []
length = []

#--------------------------------------------------------------
# 입력받은 각 job의 arrivaltime을 arrivaltime list에 저장한다.
# 입력받지 않았을 경우에는 random한 값으로 설정한다.
if options.alist == '':
    arrivaltime = [int(options.mat * random.random()) for i in range(options.jobs)]
else:
    arrivaltime = options.alist.split(',')
#--------------------------------------------------------------

if options.jlist == '':
    length = [int(options.maxlen * random.random()) + 1 for i in range(options.jobs)]
else:
    length = options.jlist.split(',')
for jobnum in range(options.jobs):
    joblist.append([jobnum, arrivaltime[jobnum], length[jobnum]])
    print('  Job', jobnum, '( arrival time = ' + str(arrivaltime[jobnum]) + ',', 'length = ' + str(length[jobnum]) + ' )')
print('\n')

if options.solve == True:
    print('** Solutions **\n')

    if options.policy == 'SJF':
        # SJF에서 각 job의 arrival time을 기준으로 정렬 후 동일한 arrival time을 지닌 job들은 length를 기준으로 정렬
        joblist = sorted(joblist, key=lambda  x : (x[1], x[2]))
        options.policy = 'FIFO'
    
    if options.policy == 'FIFO':
        thetime = 0
        print('Execution trace:')
        for job in joblist:
            thetime = max(thetime, job[1])
            print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[2], thetime + job[2]))
            thetime += job[2] # job에서 length의 index를 1에서 2로 변경하였다.

        print('\nFinal statistics:')
        t     = 0.0
        count = 0
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        start = 0.0
        for tmp in joblist:
            jobnum  = tmp[0]
            arrivaltime = tmp[1] # 해당 job의 arrivaltime
            runtime = tmp[2] # length의 index를 1에서 2로 변경하였다.
            
            # 각 job들의 arrivaltime이 서로 달라졌기 때문에 현재시각에 아직 arrive하지 못한 job이 발생할 수 있다.
            # 이 경우에 현재시각 t의 값을 실행할 job의 arrivaltime으로 변경한다.
            t = max(t, arrivaltime)

            response   = t - arrivaltime # response time = 현재시각(t) - arrivaltime
            turnaround = t + runtime - arrivaltime
            wait       = t - arrivaltime # wait time = 현재시각(t) - arrivaltime
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (jobnum, response, turnaround, wait))
            responseSum   += response
            turnaroundSum += turnaround
            waitSum       += wait
            t += runtime
            count = count + 1
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))
                     
    if options.policy == 'RR':
        print('Execution trace:')
        
        # 각 job의 arrivaltime을 기준으로 joblist를 정렬한다.
        joblist = sorted(joblist, key=lambda x : (x[1], x[0]))
        turnaround = {}
        response = {}
        lastran = {}
        wait = {}
        quantum  = float(options.quantum)
        jobcount = len(joblist)
        thetime  = joblist[0][1] # thetime의 초기값은 처음에 처리할 job의 arrivaltime으로 설정하였다.
        runlist = []
        for e in joblist:
            runlist.append(e)

        # lastran의 초기값을 joblist에서 동일한 index를 지닌 arrivaltime으로 설정하였다.
        # 이를 위해 joblist를 jobnum을 기준으로 정렬하였다.
        joblist = sorted(joblist, key=lambda x:x[0])
        for i in range(0,jobcount):
            lastran[i] = joblist[i][1]
            wait[i] = 0.0
            turnaround[i] = 0.0
            response[i] = -1

        while jobcount > 0:
            job = runlist.pop(0)

            # -----------------------
            # 현재시각 thetime을 기준으로 arrive하지 못한 job들을 runlist의 뒤로 옮긴다.
            while thetime < job[1]:
                runlist.append(job)
                job = runlist.pop(0)
            # -----------------------

            jobnum  = job[0]
            arrivaltime = job[1] # 해당 job의 arrivaltime
            runtime = float(job[2]) # 해당 job의 남은 runtime
            if response[jobnum] == -1:
                response[jobnum] = thetime - arrivaltime # response time = 현재시각(thetime) - arrivaltime
            currwait = thetime - lastran[jobnum]
            wait[jobnum] += currwait
            if runtime > quantum:
                runtime -= quantum
                ranfor = quantum
                print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))
                runlist.append([jobnum, arrivaltime, runtime])
                thetime += ranfor
            else:
                ranfor = runtime
                print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                turnaround[jobnum] = thetime + ranfor - arrivaltime
                jobcount -= 1
                thetime += ranfor
                # runlist에 job이 남아있고 다음에 처리할 job의 arrivaltime이 thetime보다 클 경우에는 thetime의 값을 해당 arrivaltime으로 변경한다.
                if len(runlist) > 0: thetime = max(thetime, runlist[0][1])
            lastran[jobnum] = thetime

        print('\nFinal statistics:')
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for i in range(0,len(joblist)):
            turnaroundSum += turnaround[i]
            responseSum += response[i]
            waitSum += wait[i]
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
        count = len(joblist)
        
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))

    if options.policy == 'STCF':
        print('Execution trace:')
        turnaround = {}
        response = {}
        lastran = {}
        wait = {}
        jobcount = len(joblist)
        for i in range(0,jobcount):
            lastran[i] = joblist[i][1]
            wait[i] = 0.0
            turnaround[i] = 0.0
            response[i] = -1

        # 각 job의 arrivaltime을 기준으로 joblist를 정렬한다.
        # 동일한 arrivaltime을 지닐 경우 length를 기준으로 정렬한다.
        joblist = sorted(joblist, key=lambda x:(x[1],x[2]))

        # 모든 job을 staylist에 넣는다.
        staylist = []
        for e in joblist: staylist.append(e)

        thetime  = staylist[0][1] # 현재시각 thetime의 초기값을 가장 먼저 처리될 job의 arrivaltime으로 설정한다.
        runlist = []
        while jobcount > 0: # 모든 job을 처리할 때까지 작동한다.

            # ----------------------------------
            # runlist에 job이 없을 경우 staylist에서 가장 앞에 있는 job을 runlist에 넣고 현재시각(thetime)의 값을 해당 job의 arrivaltime으로 변경한다.
            if len(runlist) == 0: 
                runlist.append(staylist.pop(0))
                thetime = runlist[0][1]
            # ----------------------------------

            # ----------------------------------
            # staylist에 job이 남아있는 경우 현재시각(thetime)보다 arrivaltime이 빠른 staylist의 모든 job을 pop하여 runlist에 넣는다.
            while len(staylist) > 0 and thetime >= staylist[0][1]:
                runlist.append(staylist.pop(0))
                runlist = sorted(runlist, key=lambda x:x[2])
            # ----------------------------------

            job = runlist[0] # 현재 처리할 예정인 job
            jobnum  = job[0]
            arrivaltime = job[1]
            runtime = float(job[2])

            # 해당 job이 처음 처리되는 경우 response time = 현재시각(thetime) - arrivaltime
            if response[jobnum] == -1:
                response[jobnum] = thetime - arrivaltime 
            
            if len(staylist) == 0: # staylist에 job이 없는 경우
                ranfor = runtime
                print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                turnaround[jobnum] = thetime + ranfor - arrivaltime
                jobcount -= 1
                runlist.pop(0)
                currwait = thetime - lastran[jobnum]
                wait[jobnum] += currwait
                thetime += ranfor
            else: # staylist에 job이 남아있는 경우
                check = True
                # --------------------------------------
                # 현재 처리 중인 job의 작업이 끝나기 전에 arrive하는 job을 찾고 --(1)
                # 해당 job이 arrive하는 시점에서 처리 중이던 job의 runtime이 해당 job의 runtime보다 클 경우에 --(2)
                # 처리 중이던 job을 중단하고, --(3) 방금 arrive한 job을 runlist에 추가한다. --(4)
                # 또한 runlist에 추가된 job이 있는 경우에는 runlist를 남은 runtime을 기준으로 정렬한다. --(5)
                # 추가된 job이 없는 경우에는 처리 중이던 job의 남은 runtime동안 해당 job을 처리한다. --(6)
                for next in staylist:
                    if thetime+runtime < next[1]: break # --(1)
                    if thetime+runtime > next[1]+next[2]: # --(2)
                        check = False
                        ranfor = next[1]-thetime
                        print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor)) #--(3)
                        runlist[0][2] -= next[1] - thetime
                        currwait = thetime - lastran[jobnum]
                        wait[jobnum] += currwait
                        thetime = next[1]
                        if len(staylist) > 0:
                            runlist.append(staylist.pop(0)) # --(4)
                            runlist = sorted(runlist, key=lambda x:x[2]) # --(5)
                        break
                if check: # --(6)
                    ranfor = runtime
                    print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                    turnaround[jobnum] = thetime + ranfor - arrivaltime
                    jobcount -= 1
                    runlist.pop(0)
                    currwait = thetime - lastran[jobnum]
                    wait[jobnum] += currwait
                    thetime += ranfor
            lastran[jobnum] = thetime

        print('\nFinal statistics:')
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for i in range(0,len(joblist)):
            turnaroundSum += turnaround[i]
            responseSum += response[i]
            waitSum += wait[i]
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
        count = len(joblist)
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))

    # policy의 값이 STCF가 아닐 조건을 추가하였다.
    if options.policy != 'FIFO' and options.policy != 'SJF' and options.policy != 'RR' and options.policy != 'STCF': 
        print('Error: Policy', options.policy, 'is not available.')
        sys.exit(0)
else:
    print('Compute the turnaround time, response time, and wait time for each job.')
    print('When you are done, run this program again, with the same arguments,')
    print('but with -c, which will thus provide you with the answers. You can use')
    print('-s <somenumber> or your own job list (-l 10,15,20 for example)')
    print('to generate different problems for yourself.')
    print('')
