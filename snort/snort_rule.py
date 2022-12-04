import re
import random
import os
class Snort_Rule():
    rule_actions = ['alert','block','drop','log','pass']
    rule_protocols = ['ip','icmp','tcp','udp']
    IP_RE      = re.compile(r"(?<!\d\.)(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d|(?:\.\d))(?!\/)")
    IP_CIDR_RE = re.compile(r"(?<!\d\.)(?<!\d)(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}(?!\d|(?:\.\d))")
    #Will take the last 5 characters of a digit string if the digit is longer than 5
    PORT_RE = re.compile(r"([1-9]){1}([0-9]){0,4}(?!\d)")
    RULE_RE = re.compile(r"(alert|block|drop|log|pass)(.+)(\))")

    def __init__(self,input, config):
        rules = None
        self.rules = {}
        self.ip_vars = {}
        self.port_vars = {}
        self.__set_vars__(config)
        rules = re.findall(self.RULE_RE,input)
        for i in rules:
            print(i)
            rh = self.__get_rule_header__(''.join(i))
            rp = None#self.__get_rule_params__(i)
            vl = [rh,rp]
            vlus = {self.__get_rule_name__(''.join(i)):vl}
            print(vlus)
            exit(0)
            self.rules.update(vlus)
        self.rule_parameters = {}

        self.rules, = self.__get_rule_header__(input)
        print(self.rule_header)
        exit(0)        
        self.__set_rule_parameters()
    def __get_rule_name__(self,rules_list):
        return re.search(r'(reference:)(.+?)(\;){1}',rules_list).group()

    def __set_vars__(self,config):
        if config is None:
            return
        config_dump = None
        with open(config,'r') as f:
            config_dump = f.readlines()
            f.close()
        for line in config_dump:
            if line.lower().startswith('ipvar'):
                rule_var_params = line.split()
                rule_var_params[1] = rule_var_params[1].upper()
                if not rule_var_params[1].startswith('$'):
                    rule_var_params[1] = '$' + rule_var_params[1]
                
                if rule_var_params[2] in self.ip_vars.keys():
                    self.ip_vars.update({rule_var_params[1]:self.ip_vars[rule_var_params[2]]})
                elif rule_var_params[2]:
                    if '[' in rule_var_params[2]:
                        rule_var_params[2] = rule_var_params[2].strip('[').strip(']')
                        rule_var_params[2] = rule_var_params[2].split(',') 
                        for count,elem in enumerate(rule_var_params[2]):
                            if elem in self.port_vars.keys():
                                rule_var_params[2][count] = self.port_vars[rule_var_params[2][count]]
                    self.ip_vars.update({rule_var_params[1]:rule_var_params[2]})
            elif line.lower().startswith('portvar'):
                rule_var_params = line.split()
                if not rule_var_params[1].startswith('$'):
                    rule_var_params[1] = '$' + rule_var_params[1]
                if rule_var_params[2] in self.port_vars.keys():
                    print("val found")
                    self.port_vars.update({rule_var_params[1]:self.port_vars[rule_var_params[2]]})
                elif rule_var_params[2]:
                    if '[' in rule_var_params[2]:
                        rule_var_params[2] = rule_var_params[2].strip('[').strip(']')
                        rule_var_params[2] = rule_var_params[2].split(',') 
                        for count,elem in enumerate(rule_var_params[2]):
                            if elem in self.port_vars.keys():
                                rule_var_params[2][count] = self.port_vars[rule_var_params[2][count]]
                            else:
                                rule_var_params[2][count] = int(rule_var_params[2][count])                
                    self.port_vars.update({rule_var_params[1]:rule_var_params[2]})
    
    def __get_rule_header__(self, rule):

        rule_params = rule.split('(')
        rule_params = rule_params[0].split(' ')
        rule_action = None
        rule_ip_src = None
        rule_src_p = rule_params[3]
        rule_direction = None
        rule_ip_dst = None
        rule_dst_p = rule_params[6]

        if len(rule_params) < 2:
            raise Exception("Rule is not defined...")
        
        if rule_params[0].lower() in 'ruletype':
            raise Exception("\'ruletype\' is not supported, Skipping...")
        if rule_params[0].lower() in self.rule_actions:
            rule_action = rule_params[0]
        else:
            raise Exception("No Rule Action Found, Skipping...")
        if rule_params[1].lower() in self.rule_protocols:
            rule_protocol = rule_params[1].lower
        else:
            raise Exception("No Rule Protocol Found, Skipping...")

        if rule_params[2].upper() in self.ip_vars:
            rule_ip_src = self.ip_vars[rule_params[2]]
        elif self.IP_CIDR_RE.match(rule_params[2]) or self.IP_RE.match(rule_params[2]):
            rule_ip_src = rule_params[2]
        else:
            raise Exception("No Rule Source IP Found. Do you have an undefined ipvar? Skipping...")
        if rule_params[4] in '->' or rule_params[4] in '<>':
            rule_direction = rule_params[4]
        else:
            raise Exception("No Rule Directionality Found, Skipping...")
        if rule_params[5].upper() in self.ip_vars:
            rule_ip_dst = self.ip_vars[rule_params[5]]
        elif self.IP_CIDR_RE.match(rule_params[5]) or self.IP_RE.match(rule_params[5]):
            rule_ip_dst = rule_params[5]
        else:
            print(rule_params[5])
            raise Exception("No Rule Dest IP Found. Do you have an undefined ipvar? Skipping...")
        return {'rule_action':rule_action,'rule_ip_src':rule_ip_src,'rule_src_p':rule_src_p,'rule_direction':rule_direction,'rule_ip_dst':rule_ip_dst,'rule_dst_p':rule_dst_p}
        