/*! \file
 \brief Computation of (associated) Legendre functions (fast version)
 \copyright Roelof Rietbroek 2022
 \license
 This file is part of Frommle.
 frommle is free software; you can redistribute it and/or
 modify it under the terms of the GNU Lesser General Public
 License as published by the Free Software Foundation; either
 version 3 of the License, or (at your option) any later version.

 Frommle is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public
 License along with Frommle; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

 Created by Roelof Rietbroek, 2022

 */

#include <assert.h>

#include <cmath>
#include <utility>
#include <vector>
#ifndef FR_SH_LEGENDRE_NM_HPP
#define FR_SH_LEGENDRE_NM_HPP
template <class ftype>
class Legendre_nm {
   public:
    Legendre_nm(const int nmax);
    Legendre_nm() {}
    void set(const ftype costheta, ftype pnm[]);

    inline static size_t i_from_nm(int n, int m, int nmax) {
	assert(m <= n);
	assert(n <= nmax);
	return m * (nmax + 1) - (m * (m + 1)) / 2 + n;
    }

    inline static std::pair<int, int> nm_from_i(const size_t idx,
						const int nmax) {
	int m = (3.0 + 2 * nmax) / 2 -
		std::sqrt(std::pow(3 + 2 * nmax, 2) / 4.0 - 2 * idx);
	int n = idx - (((m + 1) * (m + 2)) / 2 + m * (nmax - m)) + m + 1;
	assert(m <= n);
	assert(n <= nmax);
	return std::make_pair(n, m);
    }

    int nmax() const { return nmax_; }
    int size() const { return sz_; }

   private:
    struct alignas(64) cacheEntry {
	ftype pnmin2 = 0.0;
	ftype pnmin1 = 0.0;
	ftype pn = 0.0;
	ftype sectorial = 0.0;
    };

    int nmax_ = -1;
    size_t sz_ = 0;
    std::vector<ftype> wnn_ = {};
    std::vector<ftype> wnm_ = {};
};

template <class ftype>
Legendre_nm<ftype>::Legendre_nm(int nmax)
    : nmax_(nmax),
      sz_(i_from_nm(nmax, nmax, nmax) + 1),
      wnn_(nmax + 1),
      wnm_(sz_) {
    // precompute factors involving square roots
    wnn_[0] = 0.0;
    wnn_[1] = sqrt(3.0);
    for (int n = 2; n <= nmax_; ++n) {
	wnn_[n] = sqrt((2 * n + 1) / (2.0 * n));
    }
    for (int m = 0; m <= nmax_; ++m) {
	for (int n = m + 1; n <= nmax_; ++n) {
	    wnm_[i_from_nm(n, m, nmax_)] =
		sqrt((2 * n + 1.0) / (n + m) * (2 * n - 1.0) / (n - m));
	}
    }
}

template <class ftype>
void Legendre_nm<ftype>::set(const ftype costheta, ftype pnm[]) {
    assert(nmax_ > 0);
    assert(costheta >= -1.0 and costheta <= 1.0);

    ftype sinTheta = std::sqrt(1 - pow(costheta, 2));

    ftype numericStabilityFactor = 1e-280;

    // Loop over orders (slowly varying)
    cacheEntry L1CacheEntry;

    // initial rescaling is 1e280
    L1CacheEntry.sectorial = 1.0 / numericStabilityFactor;
    /// Initial value of the recursion
    pnm[0] = 1.0;

    size_t idx;
    for (int m = 0; m < nmax_; ++m) {
	idx = i_from_nm(m, m, nmax_);
	L1CacheEntry.pnmin2 = numericStabilityFactor;

	// compute offdiagonal element
	L1CacheEntry.pnmin1 = wnm_[idx + 1] * costheta * L1CacheEntry.pnmin2;
	pnm[idx + 1] = L1CacheEntry.pnmin1 * L1CacheEntry.sectorial;
	// loop over remaining degrees
	for (int n = m + 2; n <= nmax_; ++n) {
	    idx = i_from_nm(n, m, nmax_);

	    L1CacheEntry.pn = wnm_[idx] * (costheta * L1CacheEntry.pnmin1 -
					   L1CacheEntry.pnmin2 / wnm_[idx - 1]);
	    // write value to output vector and shift entries in the cache
	    pnm[idx] = L1CacheEntry.pn * L1CacheEntry.sectorial;
	    // shift entry to prepare for the next degree
	    L1CacheEntry.pnmin2 = L1CacheEntry.pnmin1;
	    L1CacheEntry.pnmin1 = L1CacheEntry.pn;
	}

	// Update the m+1 sectorial (applies n+1,n+1 <- n,n recursion)
	L1CacheEntry.sectorial *= wnn_[m + 1] * sinTheta;
	// also write the next sectorial to the output vector (scaled correctly)
	pnm[i_from_nm(m + 1, m + 1, nmax_)] =
	    L1CacheEntry.sectorial * numericStabilityFactor;
    }
}

#endif	/// FR_SH_LEGENDRE_NM_HPP///
