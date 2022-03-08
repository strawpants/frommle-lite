/*! \file
 \brief 
 \copyright Roelof Rietbroek 2019
 \license
 This file is part of Frommle2.
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
 */

#include<vector>
#include "cassert"
#ifndef FR_SH_LEGENDRE_HPP_
#define FR_SH_LEGENDRE_HPP_


///@brief a class which computes and caches a unnormalized Legendre polynomial
template<class ftype>
    class Legendre{
        public:
            Legendre(){}
            Legendre(int nmax):nmax_(nmax),pn_(nmax+1){}
	    const std::vector<ftype> get(const ftype costheta);
        private:
            int nmax_=-1;
            std::vector<ftype> pn_{};
    };


///@brief a class which computes and caches a unnormalized Legendre polynomial
template<class ftype>
            const std::vector<ftype> Legendre<ftype>::get(const ftype costheta){
                assert(nmax_ >0);
                if (pn_[1] == costheta){
                    ///Quick return if already computed
                    return pn_;
                }
                
                ftype pnmin1=costheta;
                ftype pnmin2=1;
                ftype pn;
                pn_[0]=pnmin2;
                pn_[1]=pnmin1;

                for(int n=2;n<=nmax_;++n){
                   pn=((2*n-1)*costheta*pnmin1-(n-1)*pnmin2)/static_cast<ftype>(n);
                   pnmin2=pnmin1;
                   pnmin1=pn;
                   pn_[n]=pn;
                }

                return pn_;
            }
            
#endif 
