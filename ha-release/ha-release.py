#!/usr/bin/python

import sys
import time
import optparse
from retrying import retry
import boto.ec2.autoscale
import boto.ec2




class Business(object):

    TAG = "marked_for_termination"

    def __init__(self, region, profile, asg):
        """
        Create connections to the AWS services required
        """
        self.region = region
        self.profile = profile
        self.asg = asg
        self.autoscale = boto.ec2.autoscale.connect_to_region(self.region, profile_name=self.profile)
        self.ec2 = boto.ec2.connect_to_region(self.region, profile_name=self.profile)
        self.elb = boto.ec2.elb.connect_to_region(self.region, profile_name=self.profile)


    def _list_instances_in_asg(self):
        """
        
        """
        groups = self.autoscale.get_all_groups([self.asg])[0]
        return self.ec2.get_all_instances([i.instance_id for i in groups.instances])


    def _list_instance_ids_in_asg(self):
        """
        List all instancess currently in the ELB
        
        :return: array of instances
        """
        return [i.instances[0].id for i in self._list_instances_in_asg()]


    def _get_desired_capacity(self):
        """
        Query the ASG for the desired instances capacity

        :return: int no of instances
        """
        groups = self.autoscale.get_all_groups([self.asg])[0]
        return int(groups.desired_capacity)


    @retry
    def _get_current_capacity(self):
        """
        Should probs use 
        except boto.exception.BotoServerError as e:
        to catch instances that are removed from the ELB
        """
        val = 0
        #print self.__list_instances_in_asg()
        for lb in self.autoscale.get_all_groups([self.asg])[0].load_balancers:
            for i in self.elb.describe_instance_health(lb, self._list_instance_ids_in_asg()):
                if i.state == 'InService':
                    val += 1
            ## This is really dodge, currently it returns the capacity of the first
            ## ELB, but it should really check all ELBs
            return val
        #return val
 


    def _mark_instances_for_termination(self):
        """
        Tag instances that are to be terminated and removed
        from the ELB
        """
        for i in self._list_instances_in_asg():
            print "marking instance for temination"
            i.instances[0].add_tag(self.TAG, "true")


    def _check_instance_health(self):
        #print self.__list_instances_in_asg()
        for lb in self.autoscale.get_all_groups()[0].load_balancers:
            for i in self.elb.describe_instance_health(lb, self._list_instance_ids_in_asg()):
                print i.state
            

    def _get_remaining_instances(self):
        inst = []
        for instance in self._list_instances_in_asg():
            if self.TAG in instance.instances[0].tags:
                if instance.instances[0].tags[self.TAG] == 'true':
                    inst.append(instance)
        return inst


    def terminate(self):
        """
        This is the where the interesting stuff happens
        """

        self._mark_instances_for_termination()
        instances = self._get_remaining_instances()

        print "Current capacity", self._get_current_capacity()
        print "Desired capacity", self._get_desired_capacity()

        ## Should check if ASG health_type == "elb"
        for instance in list(instances):

            print "Current capacity", self._get_current_capacity()
            print "Desired capacity", self._get_desired_capacity()

            while self._get_current_capacity() < self._get_desired_capacity():
                time.sleep(10)
                print "Waiting on capacity..."
            print "Terminating instance"
            instance.instances[0].terminate()
            instances.remove(instance)
            time.sleep(10)



def main():

    parser = optparse.OptionParser(
            formatter=optparse.TitledHelpFormatter(width=78),
            add_help_option=None)

    parser.add_option("-a", "--asg", dest="asg", help="Name of the Autoscaling Group")
    parser.add_option("-r", "--region", dest="region", help="Region of the Autoscaling Group")
    parser.add_option("-p", "--profile", dest="profile", help="IAM credentials profile")

    options, args = parser.parse_args(sys.argv[1:])

    if not options.asg or not options.region or not options.profile:
        print "Wrong, fail, error, etc..."
        sys.exit(1)

    Business(options.region, options.profile, options.asg).terminate()


if __name__ == '__main__':
    main()


