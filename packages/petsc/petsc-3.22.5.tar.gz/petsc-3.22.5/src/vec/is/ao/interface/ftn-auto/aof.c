#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* ao.c */
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

#include "petscao.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aoview_ AOVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aoview_ aoview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aoviewfromoptions_ AOVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aoviewfromoptions_ aoviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aodestroy_ AODESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aodestroy_ aodestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aopetsctoapplicationis_ AOPETSCTOAPPLICATIONIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aopetsctoapplicationis_ aopetsctoapplicationis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aoapplicationtopetscis_ AOAPPLICATIONTOPETSCIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aoapplicationtopetscis_ aoapplicationtopetscis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aopetsctoapplication_ AOPETSCTOAPPLICATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aopetsctoapplication_ aopetsctoapplication
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aoapplicationtopetsc_ AOAPPLICATIONTOPETSC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aoapplicationtopetsc_ aoapplicationtopetsc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aopetsctoapplicationpermuteint_ AOPETSCTOAPPLICATIONPERMUTEINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aopetsctoapplicationpermuteint_ aopetsctoapplicationpermuteint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aoapplicationtopetscpermuteint_ AOAPPLICATIONTOPETSCPERMUTEINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aoapplicationtopetscpermuteint_ aoapplicationtopetscpermuteint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aopetsctoapplicationpermutereal_ AOPETSCTOAPPLICATIONPERMUTEREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aopetsctoapplicationpermutereal_ aopetsctoapplicationpermutereal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aoapplicationtopetscpermutereal_ AOAPPLICATIONTOPETSCPERMUTEREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aoapplicationtopetscpermutereal_ aoapplicationtopetscpermutereal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aosetfromoptions_ AOSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aosetfromoptions_ aosetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aosetis_ AOSETIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aosetis_ aosetis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aocreate_ AOCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aocreate_ aocreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  aoview_(AO ao,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLOBJECT(viewer);
*ierr = AOView(
	(AO)PetscToPointer((ao) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  aoviewfromoptions_(AO ao,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = AOViewFromOptions(
	(AO)PetscToPointer((ao) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  aodestroy_(AO *ao, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(ao);
 PetscBool ao_null = !*(void**) ao ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ao);
*ierr = AODestroy(ao);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ao_null && !*(void**) ao) * (void **) ao = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(ao);
 }
PETSC_EXTERN void  aopetsctoapplicationis_(AO ao,IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLOBJECT(is);
*ierr = AOPetscToApplicationIS(
	(AO)PetscToPointer((ao) ),
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  aoapplicationtopetscis_(AO ao,IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLOBJECT(is);
*ierr = AOApplicationToPetscIS(
	(AO)PetscToPointer((ao) ),
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  aopetsctoapplication_(AO ao,PetscInt *n,PetscInt ia[], int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLINTEGER(ia);
*ierr = AOPetscToApplication(
	(AO)PetscToPointer((ao) ),*n,ia);
}
PETSC_EXTERN void  aoapplicationtopetsc_(AO ao,PetscInt *n,PetscInt ia[], int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLINTEGER(ia);
*ierr = AOApplicationToPetsc(
	(AO)PetscToPointer((ao) ),*n,ia);
}
PETSC_EXTERN void  aopetsctoapplicationpermuteint_(AO ao,PetscInt *block,PetscInt array[], int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLINTEGER(array);
*ierr = AOPetscToApplicationPermuteInt(
	(AO)PetscToPointer((ao) ),*block,array);
}
PETSC_EXTERN void  aoapplicationtopetscpermuteint_(AO ao,PetscInt *block,PetscInt array[], int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLINTEGER(array);
*ierr = AOApplicationToPetscPermuteInt(
	(AO)PetscToPointer((ao) ),*block,array);
}
PETSC_EXTERN void  aopetsctoapplicationpermutereal_(AO ao,PetscInt *block,PetscReal array[], int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLREAL(array);
*ierr = AOPetscToApplicationPermuteReal(
	(AO)PetscToPointer((ao) ),*block,array);
}
PETSC_EXTERN void  aoapplicationtopetscpermutereal_(AO ao,PetscInt *block,PetscReal array[], int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLREAL(array);
*ierr = AOApplicationToPetscPermuteReal(
	(AO)PetscToPointer((ao) ),*block,array);
}
PETSC_EXTERN void  aosetfromoptions_(AO ao, int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
*ierr = AOSetFromOptions(
	(AO)PetscToPointer((ao) ));
}
PETSC_EXTERN void  aosetis_(AO ao,IS isapp,IS ispetsc, int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
CHKFORTRANNULLOBJECT(isapp);
CHKFORTRANNULLOBJECT(ispetsc);
*ierr = AOSetIS(
	(AO)PetscToPointer((ao) ),
	(IS)PetscToPointer((isapp) ),
	(IS)PetscToPointer((ispetsc) ));
}
PETSC_EXTERN void  aocreate_(MPI_Fint * comm,AO *ao, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(ao);
 PetscBool ao_null = !*(void**) ao ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ao);
*ierr = AOCreate(
	MPI_Comm_f2c(*(comm)),ao);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ao_null && !*(void**) ao) * (void **) ao = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
