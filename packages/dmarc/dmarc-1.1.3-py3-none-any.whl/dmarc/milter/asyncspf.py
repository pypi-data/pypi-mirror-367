import dns.asyncresolver 
from spf import *

async def DNSLookup(name, qtype, tcpfallback=True, timeout=30):
    retVal = []
    try:
        qtype = qtype.upper()
        answers = await dns.asyncresolver.resolve(name, qtype, lifetime=timeout)
        for rdata in answers:
            if qtype == 'A' or qtype == 'AAAA':
                retVal.append(((name, qtype), rdata.address))
            elif qtype == 'MX':
                retVal.append(((name, qtype), (rdata.preference, rdata.exchange)))
            elif qtype == 'PTR':
                retVal.append(((name, qtype), rdata.target.to_text(True)))
            elif qtype == 'TXT' or qtype == 'SPF':
                retVal.append(((name, qtype), rdata.strings))
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN:
        pass
    except dns.exception.Timeout as x:
        raise TempError('DNS ' + str(x))
    except dns.resolver.NoNameservers as x:
        raise TempError('DNS ' + str(x))
    return retVal

async def check2(i, s, h, local=None, receiver=None, timeout=MAX_PER_LOOKUP_TIME, verbose=False, querytime=20):
    """Test an incoming MAIL FROM:<s>, from a client with ip address i.
    h is the HELO/EHLO domain name.  This is the RFC4408/7208 compliant
    pySPF2.0 interface.  The interface returns an SPF result and explanation
    only.  SMTP response codes are not returned since neither RFC 4408 nor RFC
    7208 does specify receiver policy.  Applications updated for RFC 4408 and
    RFC 7208 should use this interface.  The maximum time, in seconds, this
    function is allowed to run before a TempError is returned is controlled by
    querytime.  When set to 0 the timeout parameter (default 20 seconds)
    controls the time allowed for each DNS lookup.  When set to a non-zero
    value, it total time for all processing related to the SPF check is
    limited to querytime (default 20 seconds as recommended in RFC 7208,
    paragraph 4.6.4).

    Returns (result, explanation) where result in
    ['pass', 'permerror', 'fail', 'temperror', 'softfail', 'none', 'neutral' ].

    Example:
    #>>> check2(i='61.51.192.42', s='liukebing@bcc.com', h='bmsi.com')

    """
    res,_,exp = await query(i=i, s=s, h=h, local=local,
        receiver=receiver,timeout=timeout,verbose=verbose,querytime=querytime).check()
    return res,exp

async def check(i, s, h, local=None, receiver=None, verbose=False):
    """Test an incoming MAIL FROM:<s>, from a client with ip address i.
    h is the HELO/EHLO domain name.  This is the pre-RFC SPF Classic interface.
    Applications written for pySPF 1.6/1.7 can use this interface to allow
    pySPF2 to be a drop in replacement for older versions.  With the exception
    of result codes, performance in RFC 4408 compliant.

    Returns (result, code, explanation) where result in
    ['pass', 'unknown', 'fail', 'error', 'softfail', 'none', 'neutral' ].

    Example:
    #>>> check(i='61.51.192.42', s='liukebing@bcc.com', h='bmsi.com')

    """
    res,code,exp = await query(i=i, s=s, h=h, local=local, receiver=receiver,
        verbose=verbose).check()
    if res == 'permerror':
        res = 'unknown'
    elif res == 'tempfail':
        res =='error'
    return res, code, exp

class query(query):
    
    async def best_guess(self, spf=DEFAULT_SPF):
        """Return a best guess based on a default SPF record.
    >>> q = query('1.2.3.4','','SUPERVISION1',receiver='example.com')
    >>> q.best_guess()[0]
    'none'
        """
        if RE_TOPLAB.split(self.d)[-1]:
            return ('none', 250, '')
        pe = self.perm_error
        r,c,e = await self.check(spf)
        if r == 'permerror':    # permerror not useful for bestguess
          if self.perm_error and self.perm_error.ext:
            r,c,e = self.perm_error.ext
          else:
            r,c = 'neutral',250
          self.perm_error = pe
        return r,c,e
    
    async def check(self, spf=None):
        """
    Returns (result, mta-status-code, explanation) where result
    in ['fail', 'softfail', 'neutral' 'permerror', 'pass', 'temperror', 'none']

    Examples:
    >>> q = query(s='strong-bad@email.example.com',
    ...           h='mx.example.org', i='192.0.2.3')
    >>> q.check(spf='v=spf1 ?all')
    ('neutral', 250, 'access neither permitted nor denied')

    >>> q.check(spf='v=spf1 redirect=controlledmail.com exp=_exp.controlledmail.com')
    ('fail', 550, 'SPF fail - not authorized')
    
    >>> q.check(spf='v=spf1 ip4:192.0.0.0/8 ?all moo')
    ('permerror', 550, 'SPF Permanent Error: Unknown mechanism found: moo')

    >>> q.check(spf='v=spf1 ip4:192.0.0.n ?all')
    ('permerror', 550, 'SPF Permanent Error: Invalid IP4 address: ip4:192.0.0.n')

    >>> q.check(spf='v=spf1 ip4:192.0.2.3 ip4:192.0.0.n ?all')
    ('permerror', 550, 'SPF Permanent Error: Invalid IP4 address: ip4:192.0.0.n')

    >>> q.check(spf='v=spf1 ip6:2001:db8:ZZZZ:: ?all')
    ('permerror', 550, 'SPF Permanent Error: Invalid IP6 address: ip6:2001:db8:ZZZZ::')

    >>> q.check(spf='v=spf1 =a ?all moo')
    ('permerror', 550, 'SPF Permanent Error: Unknown qualifier, RFC 4408 para 4.6.1, found in: =a')

    >>> q.check(spf='v=spf1 ip4:192.0.0.0/8 ~all')
    ('pass', 250, 'sender SPF authorized')

    >>> q.check(spf='v=spf1 ip4:192.0.0.0/8 -all moo=')
    ('pass', 250, 'sender SPF authorized')

    >>> q.check(spf='v=spf1 ip4:192.0.0.0/8 -all match.sub-domains_9=yes')
    ('pass', 250, 'sender SPF authorized')

    >>> q.strict = False
    >>> q.check(spf='v=spf1 ip4:192.0.0.0/8 -all moo')
    ('permerror', 550, 'SPF Permanent Error: Unknown mechanism found: moo')
    >>> q.perm_error.ext
    ('pass', 250, 'sender SPF authorized')

    >>> q.strict = True
    >>> q.check(spf='v=spf1 ip4:192.1.0.0/16 moo -all')
    ('permerror', 550, 'SPF Permanent Error: Unknown mechanism found: moo')

    >>> q.check(spf='v=spf1 ip4:192.1.0.0/16 ~all')
    ('softfail', 250, 'domain owner discourages use of this host')

    >>> q.check(spf='v=spf1 -ip4:192.1.0.0/6 ~all')
    ('fail', 550, 'SPF fail - not authorized')

    # Assumes DNS available
    >>> q.check()
    ('none', 250, '')

    >>> q.check(spf='v=spf1 ip4:1.2.3.4 -a:example.net -all')
    ('fail', 550, 'SPF fail - not authorized')
    >>> q.libspf_local='ip4:192.0.2.3 a:example.org'
    >>> q.check(spf='v=spf1 ip4:1.2.3.4 -a:example.net -all')
    ('pass', 250, 'sender SPF authorized')

    >>> q.check(spf='v=spf1 ip4:1.2.3.4 -all exp=_exp.controlledmail.com')
    ('fail', 550, 'Controlledmail.com does not send mail from itself.')
    
    >>> q.check(spf='v=spf1 ip4:1.2.3.4 ?all exp=_exp.controlledmail.com')
    ('neutral', 250, 'access neither permitted nor denied')

    >>> r = query(i='list', s='office@kitterman.com', h=None)
    >>> r.check()
    ('fail', 550, 'SPF fail - not authorized')

        """
        self.mech = []        # unknown mechanisms
        # If not strict, certain PermErrors (mispelled
        # mechanisms, strict processing limits exceeded)
        # will continue processing.  However, the exception
        # that strict processing would raise is saved here
        self.perm_error = None
        self.mechanism = None
        self.void_lookups = 0
        self.options = {}

        try:
            self.lookups = 0
            if not spf:
                spf = await self.dns_spf(self.d)
                if self.verbose: self.log("top",self.d,spf)
            if self.libspf_local and spf: 
                spf = insert_libspf_local_policy(
                    spf, self.libspf_local)
            rc = await self.check1(spf, self.d, 0)
            if self.perm_error:
                # lax processing encountered a permerror, but continued
                self.perm_error.ext = rc
                raise self.perm_error
            return rc
                
        except TempError as x:
            self.prob = x.msg
            if x.mech:
                self.mech.append(x.mech)
            return ('temperror', 451, 'SPF Temporary Error: ' + str(x))
        except PermError as x:
            if not self.perm_error:
                self.perm_error = x
            self.prob = x.msg
            if x.mech:
                self.mech.append(x.mech)
            # Pre-Lentczner draft treats this as an unknown result
            # and equivalent to no SPF record.
            return ('permerror', 550, 'SPF Permanent Error: ' + str(x))
    
    async def check1(self, spf, domain, recursion):
        # spf rfc: 3.7 Processing Limits
        #
        if recursion > MAX_RECURSION:
            # This should never happen in strict mode
            # because of the other limits we check,
            # so if it does, there is something wrong with
            # our code.  It is not a PermError because there is not
            # necessarily anything wrong with the SPF record.
            if self.strict:
                raise AssertionError('Too many levels of recursion')
            # As an extended result, however, it should be
            # a PermError.
            raise PermError('Too many levels of recursion')
        try:
            try:
                tmp, self.d = self.d, domain
                return await self.check0(spf, recursion)
            finally:
                self.d = tmp
        except AmbiguityWarning as x:
            self.prob = x.msg
            if x.mech:
                self.mech.append(x.mech)
            return ('ambiguous', 000, 'SPF Ambiguity Warning: %s' % x)
    
    async def check0(self, spf, recursion):
        """Test this query information against SPF text.

        Returns (result, mta-status-code, explanation) where
        result in ['fail', 'unknown', 'pass', 'none']
        """

        if not spf:
            return ('none', 250, EXPLANATIONS['none'])

        # Split string by space, drop the 'v=spf1'.  Split by all whitespace
        # casuses things like carriage returns being treated as valid space
        # separators, so split() is not sufficient.  
        spf = spf.split(' ')
        # Catch case where SPF record has no spaces.
        # Can never happen with conforming dns_spf(), however
        # in the future we might want to give warnings
        # for common mistakes like IN TXT "v=spf1" "mx" "-all"
        # in relaxed mode.
        if spf[0].lower() != 'v=spf1':
            if self.strict > 1:
                raise AmbiguityWarning('Invalid SPF record in', self.d)
            return ('none', 250, EXPLANATIONS['none'])
        # Just to make it even more fun, the relevant piece of the ABNF for
        # term separations is *( 1*SP ( directive / modifier ) ), so it's one
        # or more spaces, not just one.  So strip empty mechanisms.
        spf = [mech for mech in spf[1:] if mech]

        # copy of explanations to be modified by exp=
        exps = self.exps
        redirect = None

        # no mechanisms at all cause unknown result, unless
        # overridden with 'default=' modifier
        #
        default = 'neutral'
        mechs = []

        modifiers = []
        # Look for modifiers
        #
        for mech in spf:
            m = RE_MODIFIER.split(mech)[1:]
            if len(m) != 2:
                mechs.append(self.validate_mechanism(mech))
                continue

            mod,arg = m
            if mod in modifiers:
                if mod == 'redirect':
                    raise PermError('redirect= MUST appear at most once',mech)
                self.note_error('%s= MUST appear at most once'%mod,mech)
                # just use last one in lax mode
            modifiers.append(mod)
            if mod == 'exp':
                # always fetch explanation to check permerrors
                if not arg:
                    raise PermError('exp has empty domain-spec:',arg)
                arg = self.expand_domain(arg)
                if arg:
                    try:
                        exp = self.get_explanation(arg)
                        if exp and not recursion:
                            # only set explanation in base recursion level
                            self.set_explanation(exp)
                    except: pass
            elif mod == 'redirect':
                self.check_lookups()
                redirect = self.expand_domain(arg)
                if not redirect:
                    raise PermError('redirect has empty domain:',arg)
            elif mod == 'default':
                # default modifier is obsolete
                if self.strict > 1:
                    raise AmbiguityWarning('The default= modifier is obsolete.')
                if not self.strict and self.default_modifier:
                    # might be an old policy, so do it anyway
                    arg = self.expand(arg)
                    # default=- is the same as default=fail
                    default = RESULTS.get(arg, default)
            elif mod == 'op':
                if not recursion:
                    for v in arg.split('.'):
                        if v: self.options[v] = True
            else:
                # spf rfc: 3.6 Unrecognized Mechanisms and Modifiers
                self.expand(m[1])       # syntax error on invalid macro

        # Evaluate mechanisms
        #
        for mech, m, arg, cidrlength, result in mechs:

            if m == 'include':
                self.check_lookups()
                d = await self.dns_spf(arg)
                if self.verbose: self.log("include",arg,d)
                res, code, txt = await self.check1(d,arg, recursion + 1)
                if res == 'pass':
                    break
                if res == 'none':
                    self.note_error(
                        'No valid SPF record for included domain: %s' %arg,
                      mech)
                res = 'neutral'
                continue
            elif m == 'all':
                break

            elif m == 'exists':
                self.check_lookups()
                try:
                    if len(await self.dns_a(arg,'A')) > 0:
                        break
                except AmbiguityWarning:
                    # Exists wants no response sometimes so don't raise
                    # the warning.
                    pass

            elif m == 'a':
                self.check_lookups()
                if self.cidrmatch(await self.dns_a(arg,self.A), cidrlength):
                    break

            elif m == 'mx':
                self.check_lookups()
                if self.cidrmatch(await self.dns_mx(arg), cidrlength):
                    break

            elif m == 'ip4':
                if self.v == 'in-addr': # match own connection type only
                    try:
                        if self.cidrmatch([arg], cidrlength): break
                    except socket.error:
                        raise PermError('syntax error', mech)

            elif m == 'ip6':
                if self.v == 'ip6': # match own connection type only
                    try:
                        if self.cidrmatch([arg], cidrlength): break
                    except socket.error:
                        raise PermError('syntax error', mech)

            elif m == 'ptr':
                self.check_lookups()
                if domainmatch(await self.validated_ptrs(), arg):
                    break

        else:
            # no matches
            if redirect:
                #Catch redirect to a non-existant SPF record.
                redirect_record = await self.dns_spf(redirect)
                if not redirect_record:
                    raise PermError('redirect domain has no SPF record',
                        redirect)
                if self.verbose: self.log("redirect",redirect,redirect_record)
                # forget modifiers on redirect
                if not recursion:
                  self.exps = dict(self.defexps)
                  self.options = {}
                return await self.check1(redirect_record, redirect, recursion)
            result = default
            mech = None

        if not recursion:       # record matching mechanism at base level
            self.mechanism = mech
        if result == 'fail':
            return (result, 550, exps[result])
        else:
            return (result, 250, exps[result])
    
    async def get_explanation(self, spec):
        """Expand an explanation."""
        if spec:
            try:
                a = await self.dns_txt(spec,ignore_void=True)
                if len(a) == 1:
                    return str(self.expand(to_ascii(a[0]), stripdot=False))
            except PermError:
                # RFC4408 6.2/4 syntax errors cause exp= to be ignored
                if self.strict > 1:
                    raise    # but report in harsh mode for record checking tools
                pass
        elif self.strict > 1:
            raise PermError('Empty domain-spec on exp=')
        # RFC4408 6.2/4 empty domain spec is ignored
        # (unless you give precedence to the grammar).
        return None
    
    async def dns_spf(self, domain):
        """Get the SPF record recorded in DNS for a specific domain
        name.  Returns None if not found, or if more than one record
        is found.
        """
        # Per RFC 4.3/1, check for malformed domain.  This produces
        # no results as a special case.
        for label in domain.split('.'):
          if not label or len(label) > 63:
            return None
        # for performance, check for most common case of TXT first
        a = [t for t in await self.dns_txt(domain) if RE_SPF.match(t)]
        if len(a) > 1:
            if self.verbose: print('cache=',self.cache)
            raise PermError('Two or more type TXT spf records found.')
        if len(a) == 1 and self.strict < 2:
            return to_ascii(a[0])
        # check official SPF type first when it becomes more popular
        if self.strict > 1:
            #Only check for Type SPF in harsh mode until it is more popular.
            try:
                b = [t for t in await self.dns_txt(domain,'SPF',ignore_void=True)
            if RE_SPF.match(t)]
            except TempError as x:
                # some braindead DNS servers hang on type 99 query
                if self.strict > 1: raise TempError(x)
                b = []
            if len(b) > 1:
                raise PermError('Two or more type SPF spf records found.')
            if len(b) == 1:
                if self.strict > 1 and len(a) == 1 and a[0] != b[0]:
                #Changed from permerror to warning based on RFC 4408 Auth 48 change
                    raise AmbiguityWarning(
'v=spf1 records of both type TXT and SPF (type 99) present, but not identical')
                return to_ascii(b[0])
        if len(a) == 1:
            return to_ascii(a[0])    # return TXT if SPF wasn't found
        if DELEGATE:    # use local record if neither found
            a = [t
              for t in await self.dns_txt(domain+'._spf.'+DELEGATE,ignore_void=True)
            if RE_SPF.match(t)
            ]
            if len(a) == 1: return to_ascii(a[0])
        return None

    ## Get list of TXT records for a domain name.
    # Any DNS library *must* return bytes (same as str in python2) for TXT
    # or SPF since there is no general decoding to unicode.  Py3dns-3.0.2
    # incorrectly attempts to convert to str using idna encoding by default.
    # We work around this by assuming any UnicodeErrors coming from py3dns
    # are from a non-ascii SPF record (incorrect in general).  Packages
    # should require py3dns != 3.0.2.
    # 
    # We cannot check for non-ascii here, because we must ignore non-SPF
    # records - even when they are non-ascii.  So we return bytes.
    # The caller does the ascii check for SPF records and explanations.
    # 
    async def dns_txt(self, domainname, rr='TXT',ignore_void=False):
        "Get a list of TXT records for a domain name."
        if domainname:
          try:
              dns_list = await self.dns(domainname, rr,ignore_void=ignore_void)
              if dns_list:
                  # a[0][:0] is '' for py3dns-3.0.2, otherwise b''
                  a = [a[0][:0].join(a) for a in dns_list if a]
                  # FIXME: workaround for error in py3dns-3.0.2
                  if isinstance(a[0],bytes):
                      return a
                  return [s.encode('utf-8') for s in a]
          # FIXME: workaround for error in py3dns-3.0.2
          except UnicodeError:
              raise PermError('Non-ascii characters found in %s record for %s'
                 %(rr,domainname))
        return []

    async def dns_mx(self, domainname):
        """Get a list of IP addresses for all MX exchanges for a
        domain name.
        """
        # RFC 4408/7208 section 5.4 "mx"
        # To prevent DoS attacks, more than 10 MX names MUST NOT be looked up
        # Changed to permerror if more than 10 exist in 7208
        mxnames = await self.dns(domainname, 'MX')
        if self.strict:
            max = MAX_MX
            if len(mxnames) > MAX_MX:
                raise PermError(
                    'More than %d MX records returned'%MAX_MX)
            if self.strict > 1:
                if len(mxnames) == 0:
                    raise AmbiguityWarning(
                        'No MX records found for mx mechanism', domainname)
        else:
            max = MAX_MX * 4
        mxnames.sort()
        return [a for mx in mxnames[:max] for a in await self.dns_a(mx[1],self.A)]

    async def dns_a(self, domainname, A='A'):
        """Get a list of IP addresses for a domainname.
        """
        if not domainname: return []
        r = await self.dns(domainname, A)
        if self.strict > 1 and len(r) == 0:
            raise AmbiguityWarning(
                    'No %s records found for'%A, domainname)
        if A == 'AAAA' and bytes is str:
          # work around pydns inconsistency plus python2 bytes/str ambiguity
          return [Bytes(ip) for ip in r]
        return r
    
    async def validated_ptrs(self):
        """Figure out the validated PTR domain names for the connect IP."""
# To prevent DoS attacks, more than 10 PTR names MUST NOT be looked up
        if self.strict:
            max = MAX_PTR
            if self.strict > 1:
                #Break out the number of PTR records returned for testing
                try:
                    ptrnames = await self.dns_ptr(self.i)
                    if len(ptrnames) > max:
                        warning = 'More than %d PTR records returned' % max
                        raise AmbiguityWarning(warning, self.c)
                    else:
                        if len(ptrnames) == 0:
                            raise AmbiguityWarning(
                                'No PTR records found for ptr mechanism', self.c)
                except:
                    raise AmbiguityWarning(
                      'No PTR records found for ptr mechanism', self.c)
        else:
            max = MAX_PTR * 4
        cidrlength = self.cidrmax
        return [p for p in (await self.dns_ptr(self.i))[:max]
            if self.cidrmatch(await self.dns_a(p,self.A),cidrlength)]

    async def dns_ptr(self, i):
        """Get a list of domain names for an IP address."""
        return await self.dns('%s.%s.arpa'%(reverse_dots(i),self.v), 'PTR')
    
    # FIXME: move to anydns
    #
    #   All types return a list of values.  TXT/SPF values are 
    #   in turn a list of strings (as bytes), as DNS supports long
    #   strings as shorter strings which must be concatenated.
    #
    async def dns(self, name, qtype, cnames=None, ignore_void=False):
        """DNS query.

        If the result is in cache, return that.  Otherwise pull the
        result from DNS, and cache ALL answers, so additional info
        is available for further queries later.

        CNAMEs are followed.

        If there is no data, [] is returned.

        pre: qtype in ['A', 'AAAA', 'MX', 'PTR', 'TXT', 'SPF']
        post: isinstance(__return__, types.ListType)

        Examples:
        >>> c = query(s='strong-bad@email.example.com',
        ...           h='parallel.kitterman.org',i='192.0.2.123')
        >>> "".join( chr(x) for x in bytearray(c.dns('parallel.kitterman.org', 'TXT')[0][0]) )
        'v=spf1 include:long.kitterman.org include:cname.kitterman.org -all'
        """
        if not name:
            raise Exception('Invalid query')
        name = str(name)
        if name.endswith('.'): name = name[:-1]
        if not reduce(lambda x, y: x and 0 < len(y) < 64, name.split('.'), True):
            return []   # invalid DNS name (too long or empty)
        name = name.lower()
        result = self.cache.get( (name, qtype), [])
        if result: return result
        cnamek = (name,'CNAME')
        cname = self.cache.get( cnamek )

        debug = self.verbose # and name.startswith('cname.')

        if cname:
            cname = cname[0]
        else:
            safe2cache = query.SAFE2CACHE
            if self.querytime < 0:
                raise TempError('DNS Error: exceeded max query lookup time')
            if self.querytime < self.timeout and self.querytime > 0:
                timeout = self.querytime
            else:
                timeout = self.timeout
            timethen = time.time()
            for k, v in await DNSLookup(name, qtype, self.strict, timeout):
                if debug: print('result=',k,v)
                # Force case insensitivity in cache, DNS servers often
                # return random case in domain part of answers.
                k = (k[0].lower(), k[1]) 
                if k == cnamek:
                    cname = v
                    result = self.cache.get( (cname, qtype), [])
                    if result: break
                if k[1] == 'CNAME' or (qtype,k[1]) in safe2cache:
                    if debug: print('addcache=',k,v)
                    self.cache.setdefault(k, []).append(v)
                    #if ans and qtype == k[1]:
                    #    self.cache.setdefault((name,qtype), []).append(v)
            result = self.cache.get( (name, qtype), [])
            if self.querytime > 0:
                self.querytime = self.querytime - (time.time()-timethen)
        if not result and cname:
            if not cnames:
                cnames = {}
            elif len(cnames) >= MAX_CNAME:
                #return result    # if too many == NX_DOMAIN
                raise PermError('Length of CNAME chain exceeds %d' % MAX_CNAME)
            cnames[name] = cname
            if cname.lower().rstrip('.') in cnames:
                if self.strict > 1: raise AmbiguityWarning('CNAME loop', cname)
            else:
                result = await self.dns(cname, qtype, cnames=cnames)
                if result:
                    self.cache[(name,qtype)] = result
        if not result and not ignore_void:
            self.void_lookups += 1
            if self.void_lookups > MAX_VOID_LOOKUPS:
                raise PermError('Void lookup limit of %d exceeded' % MAX_VOID_LOOKUPS)
        return result
