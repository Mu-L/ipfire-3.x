#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team

use strict;
# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %sambasettings = ();
my %cgisettings = ();
my %checked = ();
my %netsettings = ();
my %ovpnsettings = ();
my $message = "";
my $errormessage = "";

my @Logs = qx(ls /var/log/samba/);
my $Log =$Lang::tr{'no log selected'};

my $Status = qx(/usr/local/bin/sambactrl smbstatus);
$Status=~s/\n/<br \/>/g;

my $userentry = "";
my @user = ();
my @userline = ();
my $userfile = "${General::swroot}/samba/private/smbpasswd";
my %selected= () ;

my $defaultoption= "[Share]\npath = /var/ipfire/samba/share1\ncomment = Share - Public Access\nbrowseable = yes\nwriteable = yes\ncreate mask = 0777\ndirectory mask = 0777\npublic = yes\nforce user = samba";
my $defaultprinter= "[Printer]\ncomment = Printer public\npath = /var/spool/cups\nprinting = sysvn\nprintcap = lpstat\npublic = yes\nwritable = no\nprintable = yes";
my %printer = ();
my %shares = ();

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ovpn/settings", \%ovpnsettings);

############################################################################################################################
############################################# Samba Dienste fr Statusberprfung ##########################################

my %servicenames = ('SMB Daemon' => 'smbd','NetBIOS Nameserver' => 'nmbd');
#my %servicenames = ('SMB Daemon' => 'smbd','NetBIOS Nameserver' => 'nmbd','Winbind Daemon' => 'winbindd');

&Header::showhttpheaders();

############################################################################################################################
#################################### Initialisierung von Samba Variablen fr global Settings ###############################

$sambasettings{'WORKGRP'} = 'homeip.net';
$sambasettings{'NETBIOSNAME'} = 'IPFire';
$sambasettings{'SRVSTRING'} = 'Samba running on IPFire 2.0';
$sambasettings{'INTERFACES'} = '';
$sambasettings{'SECURITY'} = 'share';
$sambasettings{'OSLEVEL'} = '33';
$sambasettings{'GREEN'} = 'on';
$sambasettings{'BLUE'} = 'off';
$sambasettings{'ORANGE'} = 'off';
$sambasettings{'VPN'} = 'off';
$sambasettings{'WINSSRV'} = '';
$sambasettings{'WINSSUPPORT'} = 'on';
$sambasettings{'REMOTEANNOUNCE'} = '';
$sambasettings{'PASSWORDSYNC'} = 'off';
$sambasettings{'OTHERINTERFACES'} = '127.0.0.1';
$sambasettings{'GUESTACCOUNT'} = 'samba';
$sambasettings{'MAPTOGUEST'} = 'Never';
$sambasettings{'LOGLEVEL'} = '3 passdb:5 auth:5 winbind:2';
$sambasettings{'SOCKETOPTIONS'} = 'TCP_NODELAY SO_RCVBUF=8192 SO_SNDBUF=8192 SO_KEEPALIVE';
### Values that have to be initialized
$sambasettings{'ACTION'} = '';
### Samba CUPS Variablen
$sambasettings{'LOADPRINTERS'} = 'Yes';
$sambasettings{'PRINTING'} = 'cups';
$sambasettings{'PRINTCAPNAME'} = 'cups';
my $LOGLINES = '50';

################################################## Samba PDC Variablen #####################################################

$sambasettings{'LOCALMASTER'} = 'off';
$sambasettings{'DOMAINMASTER'} = 'off';
$sambasettings{'PREFERREDMASTER'} = 'off';
my $PDCOPTIONS = `cat ${General::swroot}/samba/pdc`;


############################################################################################################################

&General::readhash("${General::swroot}/samba/settings", \%sambasettings);
&Header::getcgihash(\%sambasettings);

sub refreshpage{&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );}

&Header::openpage('Samba', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################# Samba Rootskript aufrufe fr SU-Actions #######################################

if ($sambasettings{'ACTION'} eq 'smbuserdisable'){system("/usr/local/bin/sambactrl smbuserdisable $sambasettings{'NAME'}");refreshpage();}
if ($sambasettings{'ACTION'} eq 'smbuserenable'){system("/usr/local/bin/sambactrl smbuserenable $sambasettings{'NAME'}");refreshpage();}
if ($sambasettings{'ACTION'} eq 'smbuseradd'){system("/usr/local/bin/sambactrl smbuseradd $sambasettings{'USERNAME'} $sambasettings{'PASSWORD'} $sambasettings{'GROUP'} $sambasettings{'SHELL'}");refreshpage();}
if ($sambasettings{'ACTION'} eq 'smbpcadd'){system("/usr/local/bin/sambactrl smbpcadd $sambasettings{'PCNAME'} $sambasettings{'GROUP'} $sambasettings{'SHELL'}");refreshpage();}
if ($sambasettings{'ACTION'} eq 'smbchangepw'){system("/usr/local/bin/sambactrl smbchangepw $sambasettings{'USERNAME'} $sambasettings{'PASSWORD'}");refreshpage();}
if ($sambasettings{'ACTION'} eq 'smbrestart'){system("/usr/local/bin/sambactrl smbrestart");refreshpage();}
if ($sambasettings{'ACTION'} eq 'smbstart'){system("/usr/local/bin/sambactrl smbstart");refreshpage();}
if ($sambasettings{'ACTION'} eq 'smbstop'){system("/usr/local/bin/sambactrl smbstop");refreshpage();}
if ($sambasettings{'ACTION'} eq 'smbreload'){system("/usr/local/bin/sambactrl smbreload");refreshpage();}
if ($sambasettings{'ACTION'} eq 'globalresetyes')
	{
	system("/usr/local/bin/sambactrl smbglobalreset");
	$sambasettings{'WORKGRP'} = 'homeip.net';
	$sambasettings{'NETBIOSNAME'} = 'IPFire';
	$sambasettings{'SRVSTRING'} = 'Samba running on IPFire 2.0';
	$sambasettings{'INTERFACES'} = '';
	$sambasettings{'SECURITY'} = 'share';
	$sambasettings{'OSLEVEL'} = '65';
	$sambasettings{'GREEN'} = 'on';
	$sambasettings{'BLUE'} = 'off';
	$sambasettings{'ORANGE'} = 'off';
	$sambasettings{'VPN'} = 'off';
	$sambasettings{'WINSSRV'} = '';
	$sambasettings{'WINSSUPPORT'} = 'on';
	$sambasettings{'REMOTEANNOUNCE'} = '';
	$sambasettings{'PASSWORDSYNC'} = 'off';
	$sambasettings{'OTHERINTERFACES'} = '127.0.0.1';
	$sambasettings{'GUESTACCOUNT'} = 'samba';
	$sambasettings{'MAPTOGUEST'} = 'Never';
	$sambasettings{'LOGLEVEL'} = '3 passdb:5 auth:5 winbind:2';
### Samba CUPS Variablen
	$sambasettings{'LOADPRINTERS'} = 'Yes';
	$sambasettings{'PRINTING'} = 'cups';
	$sambasettings{'PRINTCAPNAME'} = 'cups';
	$sambasettings{'PRINTERNAME'} = 'Printer';
### Values that have to be initialized
	$sambasettings{'ACTION'} = '';
	$sambasettings{'LOCALMASTER'} = 'off';
	$sambasettings{'DOMAINMASTER'} = 'off';
	$sambasettings{'PREFERREDMASTER'} = 'off';
	$sambasettings{'SOCKETOPTIONS'} = 'TCP_NODELAY SO_RCVBUF=8192 SO_SNDBUF=8192 SO_KEEPALIVE';
	$PDCOPTIONS = `cat ${General::swroot}/samba/pdc`;
	system("/usr/local/bin/sambactrl smbreload");
	refreshpage();
	}

############################################################################################################################
################################################ Sicherheitsabfrage für den Reset ##########################################

if ($sambasettings{'ACTION'} eq 'globalreset')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='${Header::table1colour}' colspan='3' align='center'><b>$Lang::tr{'resetglobals'}</b>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'yes'} <input type='image' alt='$Lang::tr{'yes'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='globalresetyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'no'}' src='/images/dialog-error.png' /> $Lang::tr{'no'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

if ($sambasettings{'ACTION'} eq 'sharesreset')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='${Header::table1colour}' colspan='3' align='center'><b>$Lang::tr{'resetshares'}</b>
	<tr><td align='right'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'yes'} <input type='image' alt='$Lang::tr{'yes'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='sharesresetyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'no'}' src='/images/dialog-error.png' /> $Lang::tr{'no'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
	}

############################################################################################################################
########################################### Samba Benutzer oder PC l�chen #################################################

if ($sambasettings{'ACTION'} eq 'userdelete'){system("/usr/local/bin/sambactrl smbuserdelete $sambasettings{'NAME'}");refreshpage();}

############################################################################################################################
##################################### Umsetzen der Werte von Checkboxen und Dropdowns ######################################

if ($sambasettings{'ACTION'} eq $Lang::tr{'save'})
{
$sambasettings{'INTERFACES'} = '';
if ($sambasettings{'GREEN'} eq 'on'){ $sambasettings{'INTERFACES'} .= " $netsettings{'GREEN_DEV'}";}
if ($sambasettings{'BLUE'} eq 'on'){ $sambasettings{'INTERFACES'} .= " $netsettings{'BLUE_DEV'}";}
if ($sambasettings{'ORANGE'} eq 'on'){ $sambasettings{'INTERFACES'} .= " $netsettings{'ORANGE_DEV'}";}
if ($sambasettings{'VPN'} eq 'on'){ $sambasettings{'INTERFACES'} .= " $ovpnsettings{'DDEVICE'}";}
if ($sambasettings{'OTHERINTERFACES'} ne ''){ $sambasettings{'INTERFACES'} .= " $sambasettings{'OTHERINTERFACES'}";}

############################################################################################################################
##################################### Schreiben settings und bersetzen fr smb.conf #######################################

delete $sambasettings{'__CGI__'};delete $sambasettings{'x'};delete $sambasettings{'y'};
&General::writehash("${General::swroot}/samba/settings", \%sambasettings);

if ($sambasettings{'PASSWORDSYNC'} eq 'on'){ $sambasettings{'PASSWORDSYNC'} = "true";} else { $sambasettings{'PASSWORDSYNC'} = "false";}
if ($sambasettings{'WINSSUPPORT'} eq 'on'){ $sambasettings{'WINSSUPPORT'} = "true";$sambasettings{'WINSSRV'} = "";} else { $sambasettings{'WINSSUPPORT'} = "false";}
if ($sambasettings{'LOCALMASTER'} eq 'on'){ $sambasettings{'LOCALMASTER'} = "true";} else { $sambasettings{'LOCALMASTER'} = "false";}
if ($sambasettings{'DOMAINMASTER'} eq 'on'){ $sambasettings{'DOMAINMASTER'} = "true";} else { $sambasettings{'DOMAINMASTER'} = "false";}
if ($sambasettings{'PREFERREDMASTER'} eq 'on'){ $sambasettings{'PREFERREDMASTER'} = "true";} else { $sambasettings{'PREFERREDMASTER'} = "false";}

############################################################################################################################
############################################# Schreiben der Samba globals ##################################################

	open (FILE, ">${General::swroot}/samba/global") or die "Can't save the global settings: $!";
	flock (FILE, 2);
	
print FILE <<END
# global.settings by IPFire Project

[global]
netbios name = $sambasettings{'NETBIOSNAME'}
server string = $sambasettings{'SRVSTRING'}
workgroup = $sambasettings{'WORKGRP'}

keep alive = 30
os level = $sambasettings{'OSLEVEL'}
fstype = NTFS

kernel oplocks = false
map to guest = $sambasettings{'MAPTOGUEST'}
smb ports = 445 139
unix charset = CP850

security = $sambasettings{'SECURITY'}
encrypt passwords = yes
guest account = $sambasettings{'GUESTACCOUNT'}
unix password sync = $sambasettings{'PASSWORDSYNC'}
null passwords = yes

bind interfaces only = true
interfaces = $sambasettings{'INTERFACES'}
socket options = $sambasettings{'SOCKETOPTIONS'}
remote announce = $sambasettings{'REMOTEANNOUNCE'}

username level = 1
wins support = $sambasettings{'WINSSUPPORT'}
wins server = $sambasettings{'WINSSRV'}

log file       = /var/log/samba/samba-log.%m
lock directory = /var/lock/samba
pid directory = /var/run/
log level = $sambasettings{'LOGLEVEL'}
	
preferred master = $sambasettings{'PREFERREDMASTER'}
domain master = $sambasettings{'DOMAINMASTER'}
local master = $sambasettings{'LOCALMASTER'}

END
;
close FILE;

	if (-e "${General::swroot}/cups/enable"){
	open (FILE, ">>${General::swroot}/samba/global") or die "Can't save the global cups settings: $!";
	flock (FILE, 2);
	print FILE <<END
load printers = $sambasettings{'LOADPRINTERS'}
printing = $sambasettings{'PRINTING'}
printcap name = $sambasettings{'PRINTCAPNAME'}

END
;
close FILE;
	}

	if ($sambasettings{'SECURITY'} eq 'User' && $sambasettings{'DOMAINMASTER'} eq 'true' )
	{
	open (FILE, ">${General::swroot}/samba/pdc") or die "Can't save the pdc settings: $!";
	flock (FILE, 2);
	chomp $sambasettings{'PDCOPTIONS'};
	$sambasettings{'PDCOPTIONS'} =~ s/\r\n/\n/gi;
	$sambasettings{'PDCOPTIONS'} =~ s/^\n//gi;
	$sambasettings{'PDCOPTIONS'} =~ s/^\r//gi;
	$sambasettings{'PDCOPTIONS'} =~ s/^.\n//gi;
	$sambasettings{'PDCOPTIONS'} =~ s/^.\r//gi;
	print FILE <<END
$sambasettings{'PDCOPTIONS'}
END
;
	close FILE;
	}

if ( -e "/var/ipfire/cups/enable")
	{
	if ( $sambasettings{'SECURITY'} eq 'User' && $sambasettings{'DOMAINMASTER'} eq 'true' ){system("/usr/local/bin/sambactrl smbsafeconfpdccups");refreshpage();}
	else {system("/usr/local/bin/sambactrl smbsafeconfcups");refreshpage();}
	}
else
	{
	if ( $sambasettings{'SECURITY'} eq 'User' && $sambasettings{'DOMAINMASTER'} eq 'true' ){system("/usr/local/bin/sambactrl smbsafeconfpdc");refreshpage();}
	else{system("/usr/local/bin/sambactrl smbsafeconf");refreshpage();}
	}

system("/usr/local/bin/sambactrl smbreload");refreshpage();
}
  &General::readhash("${General::swroot}/samba/settings", \%sambasettings);
  

if ($errormessage)
	{
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
	}

############################################################################################################################
########################################## Aktivieren von Checkboxen und Dropdowns #########################################

$checked{'WINSSUPPORT'}{'off'} = '';
$checked{'WINSSUPPORT'}{'on'} = '';
$checked{'WINSSUPPORT'}{$sambasettings{'WINSSUPPORT'}} = "checked='checked'";
$checked{'PASSWORDSYNC'}{'off'} = '';
$checked{'PASSWORDSYNC'}{'on'} = '';
$checked{'PASSWORDSYNC'}{$sambasettings{'PASSWORDSYNC'}} = "checked='checked'";
$checked{'LOCALMASTER'}{'off'} = '';
$checked{'LOCALMASTER'}{'on'} = '';
$checked{'LOCALMASTER'}{$sambasettings{'LOCALMASTER'}} = "checked='checked'";
$checked{'DOMAINMASTER'}{'off'} = '';
$checked{'DOMAINMASTER'}{'on'} = '';
$checked{'DOMAINMASTER'}{$sambasettings{'DOMAINMASTER'}} = "checked='checked'";
$checked{'PREFERREDMASTER'}{'off'} = '';
$checked{'PREFERREDMASTER'}{'on'} = '';
$checked{'PREFERREDMASTER'}{$sambasettings{'PREFERREDMASTER'}} = "checked='checked'";
$checked{'GREEN'}{'off'} = '';
$checked{'GREEN'}{'on'} = '';
$checked{'GREEN'}{$sambasettings{'GREEN'}} = "checked='checked'";
$checked{'BLUE'}{'off'} = '';
$checked{'BLUE'}{'on'} = '';
$checked{'BLUE'}{$sambasettings{'BLUE'}} = "checked='checked'";
$checked{'ORANGE'}{'off'} = '';
$checked{'ORANGE'}{'on'} = '';
$checked{'ORANGE'}{$sambasettings{'ORANGE'}} = "checked='checked'";
$checked{'VPN'}{'off'} = '';
$checked{'VPN'}{'on'} = '';
$checked{'VPN'}{$sambasettings{'VPN'}} = "checked='checked'";

$selected{'MAPTOGUEST'}{$sambasettings{'MAPTOGUEST'}} = "selected='selected'";
$selected{'SECURITY'}{$sambasettings{'SECURITY'}} = "selected='selected'";

############################################################################################################################
################################### Aufbau der HTML Seite fr globale Sambaeinstellungen ###################################

&Header::openbox('100%', 'center', $Lang::tr{'samba'});
print <<END
<hr />
<br />
<table width='95%' cellspacing='0'>
END
;
if ( $message ne "" )
	{
	print "<tr><td colspan='3' align='left'><font color='red'>$message</font>";
	}

print <<END
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'all services'}</b></td></tr>
</table><table width='95%' cellspacing='0'>
END
;

my $key = '';
foreach $key (sort keys %servicenames)
	{
	print "<tr><td align='left' width='40%'>$key</td>";
	my $shortname = $servicenames{$key};
	my $status = &isrunning($shortname);
	print "$status</tr>";
	}

print <<END
</table>
<br />
<table width='95%' cellspacing='0'>
<tr><td align='left' width='40%' />
<td align='center' ><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='smbstart' /><input type='image' alt='$Lang::tr{'smbstart'}' src='/images/go-up.png' /></form></td>
<td align='center' ><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='smbstop' /><input type='image' alt='$Lang::tr{'smbstop'}' src='/images/go-down.png' /></form></td>
<td align='center' ><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='smbrestart' /><input type='image' alt='$Lang::tr{'smbrestart'}' src='/images/view-refresh.png' /></form></td></tr>
</table>
<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'basic options'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'workgroup'}</td><td align='left'><input type='text' name='WORKGRP' value='$sambasettings{'WORKGRP'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'netbios name'}</td><td align='left'><input type='text' name='NETBIOSNAME' value='$sambasettings{'NETBIOSNAME'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'server string'}</td><td align='left'><input type='text' name='SRVSTRING' value='$sambasettings{'SRVSTRING'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'log level'}</td><td align='left'><input type='text' name='LOGLEVEL' value='$sambasettings{'LOGLEVEL'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'interfaces'}</td><td align='left'>on <input type='radio' name='VPN' value='on' $checked{'VPN'}{'on'} />/
																						<input type='radio' name='VPN' value='off' $checked{'VPN'}{'off'} /> off |
																						<font size='2' color='$Header::colourovpn'><b>   OpenVpn  -  $ovpnsettings{'DDEVICE'}</b></font></td></tr>
<tr><td align='left' width='40%'></td><td align='left'>on <input type='radio' name='GREEN' value='on' $checked{'GREEN'}{'on'} />/
																	<input type='radio' name='GREEN' value='off' $checked{'GREEN'}{'off'} /> off |
																	<font size='2' color='$Header::colourgreen'><b>   $Lang::tr{'green'}  -  $netsettings{'GREEN_DEV'}</b></font></td></tr>
END
;

if (&Header::blue_used())
	{
	print <<END
	<tr><td align='left' width='40%'></td><td align='left'>on <input type='radio' name='BLUE' value='on' $checked{'BLUE'}{'on'} />/
																		<input type='radio' name='BLUE' value='off' $checked{'BLUE'}{'off'} /> off |
																		<font size='2' color='$Header::colourblue'><b>   $Lang::tr{'wireless'}  -  $netsettings{'BLUE_DEV'}</b></font></td></tr>
END
;
	}

if (&Header::orange_used())
	{
	print <<END
	<tr><td align='left' width='40%'></td><td align='left'>on <input type='radio' name='ORANGE' value='on' $checked{'ORANGE'}{'on'} />/
																		<input type='radio' name='ORANGE' value='off' $checked{'ORANGE'}{'off'} /> off |
																		<font size='2' color='$Header::colourorange'><b>   $Lang::tr{'dmz'}  -  $netsettings{'ORANGE_DEV'}</b></font></td></tr>
END
;
	}

print <<END
<tr><td align='center' width='40%'>$Lang::tr{'more'}</td><td align='left'><input type='text' name='OTHERINTERFACES' value='$sambasettings{'OTHERINTERFACES'}' size="30" /></td></tr>
<tr><td align='left'><br /></td><td></td></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'security options'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'security'}</td><td align='left'><select name='SECURITY' style="width: 165px">
																				<option value='share' $selected{'SECURITY'}{'share'}>Share</option>
																				<option value='user' $selected{'SECURITY'}{'user'}>User</option>
																				<option value='domain' $selected{'SECURITY'}{'domain'}>Domain</option>
																				<option value='ADS' $selected{'SECURITY'}{'ADS'}>ADS</option>
																				<option value='server' $selected{'SECURITY'}{'server'}>Server</option>
																				</select></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'map to guest'}</td><td align='left'><select name='MAPTOGUEST' style="width: 165px">
																						<option value='Never' $selected{'MAPTOGUEST'}{'Never'}>Never</option>
																						<option value='Bad User' $selected{'MAPTOGUEST'}{'Bad User'}>Bad User</option>
																						<option value='Bad Password' $selected{'MAPTOGUEST'}{'Bad Password'}>Bad Password</option>
																						</select></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'unix password sync'}</td><td align='left'>on <input type='radio' name='PASSWORDSYNC' value='on' $checked{'PASSWORDSYNC'}{'on'} />/
																										<input type='radio' name='PASSWORDSYNC' value='off' $checked{'PASSWORDSYNC'}{'off'} /> off</td></tr>
<tr><td align='left'><br /></td><td /></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'network options'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'os level'}</td><td align='left'><input type='text' name='OSLEVEL' value='$sambasettings{'OSLEVEL'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'socket options'}</td><td align='left'><input type='text' name='SOCKETOPTIONS' value='$sambasettings{'SOCKETOPTIONS'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'remote announce'}</td><td align='left'><input type='text' name='REMOTEANNOUNCE' value='$sambasettings{'REMOTEANNOUNCE'}' size="30" /></td></tr>
END
;
if ($sambasettings{'WINSSUPPORT'} eq 'off') {print"<tr><td align='left' width='40%'>$Lang::tr{'wins server'}</td><td align='left'><input type='text' name='WINSSRV' value='$sambasettings{'WINSSRV'}' size='30' /></td></tr>";}
	print <<END
<tr><td align='left' width='40%'>$Lang::tr{'wins support'}</td><td align='left'>on <input type='radio' name='WINSSUPPORT' value='on' $checked{'WINSSUPPORT'}{'on'} />/
																								<input type='radio' name='WINSSUPPORT' value='off' $checked{'WINSSUPPORT'}{'off'} /> off</td></tr>
END
;

if ($sambasettings{'SECURITY'} eq 'user')
	{
	print <<END
<tr><td align='left' width='40%'>$Lang::tr{'local master'}</td><td align='left'>on <input type='radio' name='LOCALMASTER' value='on' $checked{'LOCALMASTER'}{'on'} />/
																							<input type='radio' name='LOCALMASTER' value='off' $checked{'LOCALMASTER'}{'off'} /> off</td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'domain master'}</td><td align='left'>on <input type='radio' name='DOMAINMASTER' value='on' $checked{'DOMAINMASTER'}{'on'} />/
																								<input type='radio' name='DOMAINMASTER' value='off' $checked{'DOMAINMASTER'}{'off'} /> off</td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'prefered master'}</td><td align='left'>on <input type='radio' name='PREFERREDMASTER' value='on' $checked{'PREFERREDMASTER'}{'on'} />/
																									<input type='radio' name='PREFERREDMASTER' value='off' $checked{'PREFERREDMASTER'}{'off'} /> off</td></tr>
END
;
	}

if ($sambasettings{'SECURITY'} eq 'user' && $sambasettings{'DOMAINMASTER'} eq 'on')
	{
	print <<END
	<tr><td align='left'><br /></td><td></td></tr>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'pdc options'}</b></td></tr>
	<tr><td align='left'><br /></td><td></td></tr>
	<tr><td colspan='2' align='center'><textarea name="PDCOPTIONS" cols="50" rows="15" Wrap="off">$PDCOPTIONS</textarea></td></tr>
END
;
	}
	
	if ( -e "/var/ipfire/cups/enable")
	{
	print <<END
	<tr><td align='left'><br /></td><td></td></tr>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'printing options'}</b></td></tr>
	<tr><td align='left' width='40%'>$Lang::tr{'load printer'}</td><td align='left'><input type='text' name='LOADPRINTERS' value='$sambasettings{'LOADPRINTERS'}' size="30" /></td></tr>
	<tr><td align='left' width='40%'>$Lang::tr{'printing'}</td><td align='left'><input type='text' name='PRINTING' value='$sambasettings{'PRINTING'}' size="30" /></td></tr>
	<tr><td align='left' width='40%'>$Lang::tr{'printcap name'}</td><td align='left'><input type='text' name='PRINTCAPNAME' value='$sambasettings{'PRINTCAPNAME'}' size="30" /></td></tr>
END
;
	}

print <<END
</table>
<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value=$Lang::tr{'save'} />
												<input type='image' alt='$Lang::tr{'save'}' src='/images/media-floppy.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalreset' />
										<input type='image' alt='$Lang::tr{'reset'}' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalcaption' />
										<input type='image' alt='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form></td></tr>
</table>
END
;

if ($sambasettings{'ACTION'} eq 'globalcaption')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
	<tr><td align='right' width='33%'><img src='/images/media-floppy.png' /></td><td align='left'>$Lang::tr{'save settings'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/reload.gif' /></td><td align='left'>$Lang::tr{'restore settings'}</td></tr>
	</table>
END
;
	}

&Header::closebox();

############################################################################################################################
########################################## Benutzerverwaltung fr Usersecurity #############################################

if ($sambasettings{'SECURITY'} eq 'user')
	{
	if ($sambasettings{'DOMAINMASTER'} eq 'off')
		{
		&Header::openbox('100%', 'center', $Lang::tr{'accounting user nonpdc'});
		}
	else
		{
		&Header::openbox('100%', 'center', $Lang::tr{'accounting user pdc'});
		}
	print <<END
	<hr />
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td colspan='6' align='left'></td></tr>
	<tr><td bgcolor='${Header::table1colour}' colspan='7' align='left'><b>$Lang::tr{'accounting'}</b></td></tr>
	<tr><td align='left'><u>$Lang::tr{'username'}</u></td><td align='left'><u>$Lang::tr{'password'}</u></td>
END
;

	if ($sambasettings{'DOMAINMASTER'} eq 'off')
		{
		print "<td></td>";
		}
	else
		{
		print "<td align='left'><u>$Lang::tr{'type'}</u></td>";
		}

	print "<td align='left'><u>$Lang::tr{'status'}</u></td><td colspan='3' width='5%' align='center'><u>$Lang::tr{'options'}</u></td></tr>";
	system('/usr/local/bin/sambactrl readsmbpasswd');
	open(FILE, "<${General::swroot}/samba/private/smbpasswd") or die "Can't read user file: $!";
	@user = <FILE>;
	close(FILE);
	system('/usr/local/bin/sambactrl locksmbpasswd');
	foreach $userentry (sort @user)
		{
		@userline = split( /\:/, $userentry );
		print "<tr><td align='left'>$userline[0]</td><td align='left'>";
		if ($userline[4] =~ /N/)
			{
			print "$Lang::tr{'not set'}</td><td align='left'>";
			}
		else
			{
			print "$Lang::tr{'set'}</td><td align='left'>";
			}

		if ($sambasettings{'DOMAINMASTER'} eq 'off')
			{
			print "</td><td align='left'>";
			}
		else
			{
			if ($userline[0] =~ /\$/)
				{
				print "$Lang::tr{'pc'}</td><td align='left'>";
				}
			else
				{
				print "$Lang::tr{'user'}</td><td align='left'>";
				}
			}

		if ($userline[4] =~ /D/)
			{
			print <<END
			$Lang::tr{'inactive'}</td>
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='smbuserenable' />
					<input type='image' alt='$Lang::tr{'activate'}' src='/images/on.gif' />
			</form></td>
END
;
			}
		else
			{
			print <<END
			$Lang::tr{'active'}</td>
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='smbuserdisable' />
					<input type='image' alt='$Lang::tr{'deactivate'}' src='/images/off.gif' />
			</form></td>
END
;
			}

		if ($userline[0] =~ /\$/)
			{
			print "<td></td>";
			}
		else
			{
			print <<END
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='userchangepw' />
					<input type='image' alt='$Lang::tr{'edit'}' src='/images/edit.gif' />
			</form></td>
END
;
			}

			if ($sambasettings{'DOMAINMASTER'} eq 'on' && $userline[0] =~ /\$/)
				{
				print <<END
				<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='NAME' value='$userline[0]' />
						<input type='hidden' name='ACTION' value='userdelete' />
						<input type='image' alt='$Lang::tr{'delete'}' src='/images/network-error.png' />
						</form></td></tr>
END
;
				}
			else
				{
				print <<END
				<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='NAME' value='$userline[0]' />
						<input type='hidden' name='ACTION' value='userdelete' />
						<input type='image' alt='$Lang::tr{'delete'}' src='/images/user-option-remove.png' />
				</form></td></tr>
END
;
				}
		}
	print <<END
	</table>
	<br />
	<table width='10%' cellspacing='0'>
	<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
													<input type='hidden' name='ACTION' value='useradd' />
													<input type='image' alt='$Lang::tr{'add user'}' src='/images/user-option-add.png' /></form></td>
END
;

	if ($sambasettings{'DOMAINMASTER'} eq 'on')
		{
		print <<END
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='pcadd' />
												<input type='image' alt='$Lang::tr{'pc add'}' src='/images/network.png' /></form>
END
;
		}
	print <<END
	<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
											<input type='hidden' name='ACTION' value='usercaption' />
											<input type='image' alt='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form>
	</td></tr>
	</table>
END
;

	if ($sambasettings{'ACTION'} eq 'usercaption')
		{
		print <<END
		<br />
		<table width='95%' cellspacing='0'>
		<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
		<tr><td align='right' width='33%'><img src='/images/user-option-add.png' /></td><td align='left'>$Lang::tr{'add user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/network.png' /></td><td align='left'>$Lang::tr{'pc add'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/user-option-remove.png' /></td><td align='left'>$Lang::tr{'delete user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/network-error.png' /></td><td align='left'>$Lang::tr{'delete pc'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/on.gif' /></td><td align='left'>$Lang::tr{'activate user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/off.gif' /></td><td align='left'>$Lang::tr{'deactivate user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/edit.gif' /></td><td align='left'>$Lang::tr{'change passwords'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/media-floppy.png' /></td><td align='left'>$Lang::tr{'save config'}</td></tr>
		</table>
END
;
		}

	if ($sambasettings{'ACTION'} eq 'userchangepw')
		{
		my $username = "$sambasettings{'NAME'}";
		my $password = 'samba';
		print <<END
		<hr />
		<br />
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%' cellspacing='0'>
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'change passwords'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'username'}</td><td><input type='text' name='USERNAME' value='$username' size='30' readonly /></td></tr>
		<tr><td align='left'>$Lang::tr{'password'}</td><td><input type='password' name='PASSWORD' value='$password' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbchangepw' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/media-floppy.png' /></td></tr>
		</table>
		</form>
END
;
		}

	if ($sambasettings{'ACTION'} eq 'useradd')
		{
		my $username = "user";
		my $password = "samba";
		chomp $username;
		$username=~s/\s//g;
		chomp $password;
		$password=~s/\s//g;
		print <<END
		<hr />
		<br />
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%' cellspacing='0'>
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'add user'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'username'}</td><td><input type='text' name='USERNAME' value='$username' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'password'}</td><td><input type='password' name='PASSWORD' value='$password' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix group'}</td><td><input type='text' name='GROUP' value='sambauser' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix shell'}</td><td><input type='text' name='SHELL' value='/bin/false' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbuseradd' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/media-floppy.png' /></td></tr>
		</table>
		</form>
END
;
		}

	if ($sambasettings{'ACTION'} eq 'pcadd')
		{
		my $pcname = "client\$";
		chomp $pcname;
		$pcname=~s/\s//g;
		print <<END
		<hr />
		<br />
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%' cellspacing='0'>
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'pc add'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'client'}</td><td><input type='text' name='PCNAME' value='$pcname' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix group'}</td><td><input type='text' name='GROUP' value='sambawks' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix shell'}</td><td><input type='text' name='SHELL' value='/bin/false' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbpcadd' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/media-floppy.png' /></td></tr>
		</table>
		</form>
END
;
		}

&Header::closebox();
}

############################################################################################################################
############################################### Verwalten von Freigaben ####################################################

&Header::openbox('100%', 'center', $Lang::tr{'shares'});

my %shares =  config("${General::swroot}/samba/shares");


print <<END
<hr />
<br />
<table width='95%' cellspacing='0'>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>$Lang::tr{'manage shares'}</b>
<tr><td align='left'><u>$Lang::tr{'sharename'}</u></td><td colspan='2' width="5%" align='center'><u>$Lang::tr{'options'}</u></td></tr>
END
;

my @Shares = keys(%shares);

foreach my $shareentry (sort @Shares)
	{
	chomp $shareentry;
	print <<END
	<tr><td align='left'>$shareentry</td>
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$shareentry' />
			<input type='hidden' name='ACTION' value='sharechange' />
			<input type='image' alt='$Lang::tr{'edit'}' src='/images/edit.gif' />
	</form></td>
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$shareentry' />
			<input type='hidden' name='ACTION' value='smbsharedel' />
			<input type='image' alt='$Lang::tr{'delete'}' src='/images/user-trash.png' />
	</form></td></tr>
END
;
	}

print <<END
</table>
<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='shareadd' />
												<input type='image' alt='$Lang::tr{'add share'}' src='/images/list-add.png' />
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='sharesreset' />
												<input type='image' alt='$Lang::tr{'reset'}' src='/images/reload.gif' />
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='sharecaption' />
												<input type='image' alt='$Lang::tr{'caption'}' src='/images/help-browser.png' />
												</form></td>
</tr>
</table>
END
;

if ($sambasettings{'ACTION'} eq 'sharecaption')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
	<tr><td align='right' width='33%'><img src='/images/list-add.png' /></td><td align='left'>$Lang::tr{'add share'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/edit.gif' /></td><td align='left'>$Lang::tr{'edit share'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/media-floppy.png' /></td><td align='left'>$Lang::tr{'save config'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/reload.gif' /></td><td align='left'>$Lang::tr{'reset shares'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/user-trash.png' /></td><td align='left'>$Lang::tr{'delete share'}</td></tr>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'shareadd' || $sambasettings{'ACTION'} eq 'optioncaption' )
	{
	print <<END
	<hr />
	<br />
	<table width='95%' cellspacing='0'>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'add share'}</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'>$Lang::tr{'show share options'}
 <a href="sambahlp.cgi" target="popup" onClick="window.open ('', 'popup', 'width=580,height=600,scrollbars=yes, toolbar=no,status=no, resizable=yes,menubar=no,location=no,directories=no,top=10,left=10')"><img border="0" src="/images/help-browser.png"></a></td></tr>
	<form method='post' action='$ENV{'SCRIPT_NAME'}'><tr><td colspan='2' align='center'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$defaultoption</textarea></td></tr>
	</table>
	<br />
	<table width='10%' cellspacing='0'>
	<tr><td align='center'><input type='hidden' name='ACTION' value='smbshareadd' />
													<input type='image' alt='$Lang::tr{'add share'}' src='/images/media-floppy.png' /></td></tr></form>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'sharechange' || $sambasettings{'ACTION'} eq 'optioncaption2' )
	{
	my $shareoption = $shares{$sambasettings{'NAME'}};
	print <<END
	<hr />
	<br />
	<table width='95%' cellspacing='0'>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'edit share'}</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'>$Lang::tr{'show share options'}<a href="sambahlp.cgi" target="popup" onClick="window.open ('', 'popup', 'width=580,height=600,scrollbars=yes, toolbar=no,status=no, resizable=yes,menubar=no,location=no,directories=no,top=10,left=10')"><img border="0" src="/images/help-browser.png"></a></td></tr>
	<tr><td colspan='2' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$shareoption</textarea></td></tr>
	</table>
	<br />
	<table width='10%' cellspacing='0'>
	<tr><td align='center'><input type='hidden' name='NAME' value='$sambasettings{'NAME'}' />
													<input type='image' alt='$Lang::tr{'change share'}' src='/images/media-floppy.png' />
													<input type='hidden' name='ACTION' value='smbsharechange' /></form></td></tr>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'sharesresetyes')
	{
	system('/usr/local/bin/sambactrl smbsharesreset');
	my $shares = config("${General::swroot}/samba/shares");
	system("/usr/local/bin/sambactrl smbreload");
	}
if ($sambasettings{'ACTION'} eq 'smbshareadd')
	{
	$shares{'xvx'}= "$sambasettings{'SHAREOPTION'}";
	save("shares");
	my $shares = config("${General::swroot}/samba/shares");
	}
if ($sambasettings{'ACTION'} eq 'smbsharedel')
	{
	delete $shares{$sambasettings{'NAME'}};
	save("shares");
	my %shares = config("${General::swroot}/samba/shares");
	}
if ($sambasettings{'ACTION'} eq 'smbsharechange')
	{
	$shares{$sambasettings{'NAME'}} = $sambasettings{'SHAREOPTION'};
	save("shares");
	my %shares = config("${General::swroot}/samba/shares");
	}

&Header::closebox();

############################################################################################################################
################################################ Verwalten von Druckern ####################################################

my %printer =  config("${General::swroot}/samba/printer");

if ( -e "/var/ipfire/cups/enable")
{
&Header::openbox('100%', 'center', $Lang::tr{'printer'});

my @Printers = keys(%printer);
print <<END
<hr />
<br />
<table width='95%' cellspacing='0'>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>$Lang::tr{'manage printers'}</b>
<tr><td align='left'><u>$Lang::tr{'printername'}</u></td><td colspan='2' width="5%" align='center'><u>$Lang::tr{'options'}</u></td></tr>
END
;
foreach my $printerentry (sort @Printers)
	{
	chomp $printerentry;
	print <<END
	<tr><td align='left'>$printerentry</td>
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$printerentry' />
			<input type='hidden' name='ACTION' value='printerchange' />
			<input type='image' alt='$Lang::tr{'edit'}' src='/images/edit.gif' />
	</form></td>
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$printerentry' />
			<input type='hidden' name='ACTION' value='smbprinterdel' />
			<input type='image' alt='$Lang::tr{'delete'}' src='/images/user-trash.png' />
	</form></td></tr>
END
;
	}
print <<END
</table>
<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='printeradd' />
												<input type='image' alt='$Lang::tr{'add printer'}' src='/images/list-add.png' />
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='printereset' />
												<input type='image' alt='$Lang::tr{'reset'}' src='/images/reload.gif' />
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='printercaption' />
												<input type='image' alt='$Lang::tr{'caption'}' src='/images/help-browser.png' />
												</form></td>
</tr>
</table>
END
;

if ($sambasettings{'ACTION'} eq 'printeradd' || $sambasettings{'ACTION'} eq 'printercaption' )
	{
	print <<END
	<hr />
	<br />
	<table width='95%' cellspacing='0'>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'add printer'}</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'>$Lang::tr{'show share options'}
 <a href="sambahlp.cgi" target="popup" onClick="window.open ('', 'popup', 'width=580,height=600,scrollbars=yes, toolbar=no,status=no, resizable=yes,menubar=no,location=no,directories=no,top=10,left=10')"><img border="0" src="/images/help-browser.png"></a></td></tr>
	<form method='post' action='$ENV{'SCRIPT_NAME'}'><tr><td colspan='2' align='center'><textarea name="PRINTEROPTION" cols="50" rows="15" Wrap="off">$defaultprinter</textarea></td></tr>
	</table>
	<br />
	<table width='10%' cellspacing='0'>
	<tr><td align='center'><input type='hidden' name='ACTION' value='smbprinteradd' />
													<input type='image' alt='$Lang::tr{'add share'}' src='/images/media-floppy.png' /></td></tr>
	</table>
	</form>
END
;
	}
	
if ($sambasettings{'ACTION'} eq 'printerchange' || $sambasettings{'ACTION'} eq 'printercaption2' )
	{
	my $printeroption = $printer{$sambasettings{'NAME'}};
	print <<END
	<hr />
	<br />
	<table width='95%' cellspacing='0'>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'edit printer'}</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'>$Lang::tr{'show share options'}<a href="sambahlp.cgi" target="popup" onClick="window.open ('', 'popup', 'width=580,height=600,scrollbars=yes, toolbar=no,status=no, resizable=yes,menubar=no,location=no,directories=no,top=10,left=10')"><img border="0" src="/images/help-browser.png"></a></td></tr>
	<tr><td colspan='2' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><textarea name="PRINTEROPTION" cols="50" rows="15" Wrap="off">$printeroption</textarea></td></tr>
	</table>
	<br />
	<table width='10%' cellspacing='0'>
	<tr><td align='center'><input type='hidden' name='NAME' value='$sambasettings{'NAME'}' />
													<input type='image' alt='$Lang::tr{'change share'}' src='/images/media-floppy.png' />
													<input type='hidden' name='ACTION' value='smbprinterchange' /></form></td></tr>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'smbprinteradd')
	{
	$printer{'xvx'}= "$sambasettings{'PRINTEROPTION'}";
	save("printer");
	my %printer = config("${General::swroot}/samba/printer");
	}

if ($sambasettings{'ACTION'} eq 'smbprinterdel')
	{
	delete $printer{$sambasettings{'NAME'}};
	save("printer");
	my %printer = config("${General::swroot}/samba/printer");
	}

if ($sambasettings{'ACTION'} eq 'smbprinterchange')
	{
	$printer{$sambasettings{'NAME'}} = $sambasettings{'PRINTEROPTION'};
	save("printer");
	my %printer = config("${General::swroot}/samba/printer");
	}

&Header::closebox();
}

############################################################################################################################
############################################### Anzeige des Sambastatus ####################################################

&Header::openbox('100%', 'center', 'Status');

print <<END
<hr />
<br />
<table width='95%' cellspacing='0'>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>$Lang::tr{'samba status'}</b></td></tr>
<tr><td  align='left'>$Status</td></tr>
</table>
END
;
&Header::closebox();

############################################################################################################################
############################################### Anzeige der Sambalogs ######################################################


if ($sambasettings{'ACTION'} eq 'showlog')
{
$Log = qx(tail -n $sambasettings{'LOGLINES'} /var/log/samba/$sambasettings{'LOG'});
$Log=~s/\n/<br \/>/g;
}

&Header::openbox('100%', 'center', $Lang::tr{'log'});

print <<END
<hr />
<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>$Lang::tr{'log view'}</b></td></tr>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td  align='left'><select name='LOG' style="width: 200px">
END
;
foreach my $log (@Logs) {chomp $log;print"<option value='$log'>$log</option>";}
print <<END

</select></td><td  align='left'>$Lang::tr{'show last x lines'}<input type='text' name='LOGLINES' value='$LOGLINES' size="3" /></td>
			<td  align='left'><input type='hidden' name='ACTION' value='showlog' /><input type='image' alt='view Log' src='/images/format-justify-fill.png' /></td></tr>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td colspan='3'  align='left'><font size=2>$Log</font></td></tr>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td colspan='3'  align='center'>$sambasettings{'LOG'}</td></tr>
</table>
</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################ Subfunktion fr Sambadienste ###################################################

sub config
{
my $file = shift;
my @allarray = `grep -n '^\\[' $file`;
my @linesarray = ();
my @namearray = ();
my %hash = ();
my $options = ();
my $EOF = qx(cat $file | wc -l);
foreach my $allarrayentry (@allarray)
 {
 my @allarrayline = split( /\:/, $allarrayentry );
 push(@linesarray,$allarrayline[0]);$allarrayline[1]=~s/\[//g;$allarrayline[1]=~s/\]//g;push(@namearray,$allarrayline[1]);
 }
	for(my $i = 0; $i <= $#namearray; $i++)
		{
		chomp $namearray[$i];
		$namearray[$i]=~s/\[//g;$namearray[$i]=~s/\]//g;
		if ( $i eq $#namearray )
			{
			my $lineend = $EOF-$linesarray[$i]+1;
			$options=qx(tail -$lineend $file);
			}
		else
			{
			my $linestart = $EOF-$linesarray[$i]+1;
			my $lineend =  $linesarray[$i+1]-$linesarray[$i];
			$options=qx(tail -$linestart $file | head -$lineend);
			}
		$hash{$namearray[$i]} = "$options";
		#print"<pre>$namearray[$i]\n$options\n</pre>"; # enable only for debuging
		}
return(%hash);
}

sub save
{
my $smb = shift;
open (FILE, ">${General::swroot}/samba/$smb") or die "Can't $smb settings $!";
flock (FILE, 2);

if ( $smb eq 'printer')
	{while (my ($name, $option) = each %printer){chomp $option;$option =~ s/\r\n/\n/gi;$option =~ s/^\n//gi;$option =~ s/^\r//gi;$option =~ s/^.\n//gi;$option =~ s/^.\r//gi;print FILE "$option\n";}}

if ( $smb eq 'shares')
	{while (my ($name, $option) = each %shares){chomp $option;$option =~ s/\r\n/\n/gi;$option =~ s/^\n//gi;$option =~ s/^\r//gi;$option =~ s/^.\n//gi;$option =~ s/^.\r//gi;print FILE "$option\n";}	}

close FILE;

if ( -e "/var/ipfire/cups/enable")
	{
	if ( $sambasettings{'SECURITY'} eq 'User' && $sambasettings{'DOMAINMASTER'} eq 'true' ){system("/usr/local/bin/sambactrl smbsafeconfpdccups");}
	else {system("/usr/local/bin/sambactrl smbsafeconfcups");}
	}
else
	{
	if ( $sambasettings{'SECURITY'} eq 'User' && $sambasettings{'DOMAINMASTER'} eq 'true' ){system("/usr/local/bin/sambactrl smbsafeconfpdc");}
	else{system("/usr/local/bin/sambactrl smbsafeconf");}
	}

system("/usr/local/bin/sambactrl smbreload");
refreshpage();
}

sub isrunning
	{
	my $cmd = $_[0];
	my $status = "<td align='center' bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td>";
	my $pid = '';
	my $testcmd = '';
	my $exename;

	$cmd =~ /(^[a-z]+)/;
	$exename = $1;

	if (open(FILE, "/var/run/${cmd}.pid"))
		{
		$pid = <FILE>; chomp $pid;
		close FILE;
		if (open(FILE, "/proc/${pid}/status"))
			{
			while (<FILE>)
				{
				if (/^Name:\W+(.*)/)
					{
					$testcmd = $1; 
					}
				}
			close FILE;
			if ($testcmd =~ /$exename/)
				{
				$status = "<td align='center' bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td>";
				}
			}
		}
	return $status;
	}
