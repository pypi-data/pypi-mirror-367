#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* strumpack.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetreordering_ MATSTRUMPACKSETREORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetreordering_ matstrumpacksetreordering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetreordering_ MATSTRUMPACKGETREORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetreordering_ matstrumpackgetreordering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetcolperm_ MATSTRUMPACKSETCOLPERM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetcolperm_ matstrumpacksetcolperm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetcolperm_ MATSTRUMPACKGETCOLPERM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetcolperm_ matstrumpackgetcolperm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetgpu_ MATSTRUMPACKSETGPU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetgpu_ matstrumpacksetgpu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetgpu_ MATSTRUMPACKGETGPU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetgpu_ matstrumpackgetgpu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetcompression_ MATSTRUMPACKSETCOMPRESSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetcompression_ matstrumpacksetcompression
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetcompression_ MATSTRUMPACKGETCOMPRESSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetcompression_ matstrumpackgetcompression
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetcompreltol_ MATSTRUMPACKSETCOMPRELTOL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetcompreltol_ matstrumpacksetcompreltol
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetcompreltol_ MATSTRUMPACKGETCOMPRELTOL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetcompreltol_ matstrumpackgetcompreltol
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetcompabstol_ MATSTRUMPACKSETCOMPABSTOL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetcompabstol_ matstrumpacksetcompabstol
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetcompabstol_ MATSTRUMPACKGETCOMPABSTOL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetcompabstol_ matstrumpackgetcompabstol
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetcompleafsize_ MATSTRUMPACKSETCOMPLEAFSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetcompleafsize_ matstrumpacksetcompleafsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetcompleafsize_ MATSTRUMPACKGETCOMPLEAFSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetcompleafsize_ matstrumpackgetcompleafsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetgeometricnxyz_ MATSTRUMPACKSETGEOMETRICNXYZ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetgeometricnxyz_ matstrumpacksetgeometricnxyz
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetgeometriccomponents_ MATSTRUMPACKSETGEOMETRICCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetgeometriccomponents_ matstrumpacksetgeometriccomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetgeometricwidth_ MATSTRUMPACKSETGEOMETRICWIDTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetgeometricwidth_ matstrumpacksetgeometricwidth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetcompminsepsize_ MATSTRUMPACKSETCOMPMINSEPSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetcompminsepsize_ matstrumpacksetcompminsepsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetcompminsepsize_ MATSTRUMPACKGETCOMPMINSEPSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetcompminsepsize_ matstrumpackgetcompminsepsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetcomplossyprecision_ MATSTRUMPACKSETCOMPLOSSYPRECISION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetcomplossyprecision_ matstrumpacksetcomplossyprecision
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetcomplossyprecision_ MATSTRUMPACKGETCOMPLOSSYPRECISION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetcomplossyprecision_ matstrumpackgetcomplossyprecision
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpacksetcompbutterflylevels_ MATSTRUMPACKSETCOMPBUTTERFLYLEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpacksetcompbutterflylevels_ matstrumpacksetcompbutterflylevels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstrumpackgetcompbutterflylevels_ MATSTRUMPACKGETCOMPBUTTERFLYLEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstrumpackgetcompbutterflylevels_ matstrumpackgetcompbutterflylevels
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matstrumpacksetreordering_(Mat F,MatSTRUMPACKReordering *reordering, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetReordering(
	(Mat)PetscToPointer((F) ),*reordering);
}
PETSC_EXTERN void  matstrumpackgetreordering_(Mat F,MatSTRUMPACKReordering *reordering, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKGetReordering(
	(Mat)PetscToPointer((F) ),reordering);
}
PETSC_EXTERN void  matstrumpacksetcolperm_(Mat F,PetscBool *cperm, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetColPerm(
	(Mat)PetscToPointer((F) ),*cperm);
}
PETSC_EXTERN void  matstrumpackgetcolperm_(Mat F,PetscBool *cperm, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKGetColPerm(
	(Mat)PetscToPointer((F) ),cperm);
}
PETSC_EXTERN void  matstrumpacksetgpu_(Mat F,PetscBool *gpu, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetGPU(
	(Mat)PetscToPointer((F) ),*gpu);
}
PETSC_EXTERN void  matstrumpackgetgpu_(Mat F,PetscBool *gpu, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKGetGPU(
	(Mat)PetscToPointer((F) ),gpu);
}
PETSC_EXTERN void  matstrumpacksetcompression_(Mat F,MatSTRUMPACKCompressionType *comp, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetCompression(
	(Mat)PetscToPointer((F) ),*comp);
}
PETSC_EXTERN void  matstrumpackgetcompression_(Mat F,MatSTRUMPACKCompressionType *comp, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKGetCompression(
	(Mat)PetscToPointer((F) ),comp);
}
PETSC_EXTERN void  matstrumpacksetcompreltol_(Mat F,PetscReal *rtol, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetCompRelTol(
	(Mat)PetscToPointer((F) ),*rtol);
}
PETSC_EXTERN void  matstrumpackgetcompreltol_(Mat F,PetscReal *rtol, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLREAL(rtol);
*ierr = MatSTRUMPACKGetCompRelTol(
	(Mat)PetscToPointer((F) ),rtol);
}
PETSC_EXTERN void  matstrumpacksetcompabstol_(Mat F,PetscReal *atol, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetCompAbsTol(
	(Mat)PetscToPointer((F) ),*atol);
}
PETSC_EXTERN void  matstrumpackgetcompabstol_(Mat F,PetscReal *atol, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLREAL(atol);
*ierr = MatSTRUMPACKGetCompAbsTol(
	(Mat)PetscToPointer((F) ),atol);
}
PETSC_EXTERN void  matstrumpacksetcompleafsize_(Mat F,PetscInt *leaf_size, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetCompLeafSize(
	(Mat)PetscToPointer((F) ),*leaf_size);
}
PETSC_EXTERN void  matstrumpackgetcompleafsize_(Mat F,PetscInt *leaf_size, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLINTEGER(leaf_size);
*ierr = MatSTRUMPACKGetCompLeafSize(
	(Mat)PetscToPointer((F) ),leaf_size);
}
PETSC_EXTERN void  matstrumpacksetgeometricnxyz_(Mat F,PetscInt *nx,PetscInt *ny,PetscInt *nz, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetGeometricNxyz(
	(Mat)PetscToPointer((F) ),*nx,*ny,*nz);
}
PETSC_EXTERN void  matstrumpacksetgeometriccomponents_(Mat F,PetscInt *nc, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetGeometricComponents(
	(Mat)PetscToPointer((F) ),*nc);
}
PETSC_EXTERN void  matstrumpacksetgeometricwidth_(Mat F,PetscInt *w, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetGeometricWidth(
	(Mat)PetscToPointer((F) ),*w);
}
PETSC_EXTERN void  matstrumpacksetcompminsepsize_(Mat F,PetscInt *min_sep_size, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetCompMinSepSize(
	(Mat)PetscToPointer((F) ),*min_sep_size);
}
PETSC_EXTERN void  matstrumpackgetcompminsepsize_(Mat F,PetscInt *min_sep_size, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLINTEGER(min_sep_size);
*ierr = MatSTRUMPACKGetCompMinSepSize(
	(Mat)PetscToPointer((F) ),min_sep_size);
}
PETSC_EXTERN void  matstrumpacksetcomplossyprecision_(Mat F,PetscInt *lossy_prec, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetCompLossyPrecision(
	(Mat)PetscToPointer((F) ),*lossy_prec);
}
PETSC_EXTERN void  matstrumpackgetcomplossyprecision_(Mat F,PetscInt *lossy_prec, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLINTEGER(lossy_prec);
*ierr = MatSTRUMPACKGetCompLossyPrecision(
	(Mat)PetscToPointer((F) ),lossy_prec);
}
PETSC_EXTERN void  matstrumpacksetcompbutterflylevels_(Mat F,PetscInt *bfly_lvls, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatSTRUMPACKSetCompButterflyLevels(
	(Mat)PetscToPointer((F) ),*bfly_lvls);
}
PETSC_EXTERN void  matstrumpackgetcompbutterflylevels_(Mat F,PetscInt *bfly_lvls, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLINTEGER(bfly_lvls);
*ierr = MatSTRUMPACKGetCompButterflyLevels(
	(Mat)PetscToPointer((F) ),bfly_lvls);
}
#if defined(__cplusplus)
}
#endif
