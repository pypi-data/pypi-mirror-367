#
# spec file for package python-sitelib
#
# Copyright (c) 2023 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%files
%license COPYING
%doc ChangeLog README
%{python_sitelib}/sitelib-python
%{python_sitelib}/sitelib-python-%{version}*-info
%{python_sitearch}/sitelib-python
%{python_sitearch}/sitelib-python-%{version}*-info
%{python3_sitearch}/sitelib-python
%{python3_sitearch}/sitelib-python-%{version}*-info

%changelog
