#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dacorn.c */
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

#include "petscdmda.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdasetfieldname_ DMDASETFIELDNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdasetfieldname_ dmdasetfieldname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdagetfieldname_ DMDAGETFIELDNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdagetfieldname_ dmdagetfieldname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdasetcoordinatename_ DMDASETCOORDINATENAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdasetcoordinatename_ dmdasetcoordinatename
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdagetcoordinatename_ DMDAGETCOORDINATENAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdagetcoordinatename_ dmdagetcoordinatename
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdagetcorners_ DMDAGETCORNERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdagetcorners_ dmdagetcorners
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdagetreduceddmda_ DMDAGETREDUCEDDMDA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdagetreduceddmda_ dmdagetreduceddmda
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdacreatecompatibledmda_ DMDACREATECOMPATIBLEDMDA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdacreatecompatibledmda_ dmdacreatecompatibledmda
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmdasetfieldname_(DM da,PetscInt *nf, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(da);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMDASetFieldName(
	(DM)PetscToPointer((da) ),*nf,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmdagetfieldname_(DM da,PetscInt *nf, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(da);
*ierr = DMDAGetFieldName(
	(DM)PetscToPointer((da) ),*nf,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  dmdasetcoordinatename_(DM dm,PetscInt *nf, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMDASetCoordinateName(
	(DM)PetscToPointer((dm) ),*nf,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmdagetcoordinatename_(DM dm,PetscInt *nf, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMDAGetCoordinateName(
	(DM)PetscToPointer((dm) ),*nf,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  dmdagetcorners_(DM da,PetscInt *x,PetscInt *y,PetscInt *z,PetscInt *m,PetscInt *n,PetscInt *p, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
CHKFORTRANNULLINTEGER(x);
CHKFORTRANNULLINTEGER(y);
CHKFORTRANNULLINTEGER(z);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(p);
*ierr = DMDAGetCorners(
	(DM)PetscToPointer((da) ),x,y,z,m,n,p);
}
PETSC_EXTERN void  dmdagetreduceddmda_(DM da,PetscInt *nfields,DM *nda, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
PetscBool nda_null = !*(void**) nda ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(nda);
*ierr = DMDAGetReducedDMDA(
	(DM)PetscToPointer((da) ),*nfields,nda);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! nda_null && !*(void**) nda) * (void **) nda = (void *)-2;
}
PETSC_EXTERN void  dmdacreatecompatibledmda_(DM da,PetscInt *nfields,DM *nda, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
PetscBool nda_null = !*(void**) nda ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(nda);
*ierr = DMDACreateCompatibleDMDA(
	(DM)PetscToPointer((da) ),*nfields,nda);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! nda_null && !*(void**) nda) * (void **) nda = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
